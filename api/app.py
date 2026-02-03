from sqlalchemy import func
from dataclasses import asdict
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from quality_calculator import compute_Q, suggest_improvements, get_quality_level
from feature_analyzer import estimate_features
from variant_generator import generate_variants_logic
from prompt_optimizer import (
    optimize_prompt,
    estimate_optimization_cost,
    generate_optimization_report,
    OptimizationStrategy
)
from generate_response import generate_response, estimate_cost as estimate_llm_cost, compare_providers
import datetime
import json
import os
import logging

# Configure logging for robustness
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database Configuration
# Fallback to SQLite if DATABASE_URL is not set
default_db = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'prompts.db')}"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PromptModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    tags_json = db.Column(db.Text, default='[]')
    q_score = db.Column(db.Float, nullable=False, index=True)
    features_json = db.Column(db.Text, nullable=False)
    version = db.Column(db.Integer, default=1)
    parent_id = db.Column(db.Integer, db.ForeignKey('prompt_model.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

    @property
    def tags(self):
        return json.loads(self.tags_json)

    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value)

    @property
    def features(self):
        return json.loads(self.features_json)

    @features.setter
    def features(self, value):
        self.features_json = json.dumps(value)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "tags": self.tags,
            "Q_score": self.q_score,
            "features": self.features,
            "version": self.version,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat()
        }

with app.app_context():
    db.create_all()

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat(), "mode": "bolt ⚡"})

# ============================================================================
# PROMPT MANAGEMENT ENDPOINTS
# ============================================================================


def get_prompt_or_404(prompt_id: int) -> PromptModel:
    """Utility to fetch a prompt or abort with 404."""
    prompt = PromptModel.query.get(prompt_id)
    if not prompt:
        abort(404, description=f"Prompt {prompt_id} not found")
    return prompt

@app.route('/api/prompts/bulk', methods=['POST'])
def bulk_process():
    """Bolt ⚡ high-performance batch processing"""
    data = request.json
    prompts_data = data.get('prompts', [])
    results = []

    for item in prompts_data:
        text = item.get('text', '')
        features = estimate_features(text)
        Q_score, _ = compute_Q(features)
        results.append({
            "text": text,
            "Q_score": Q_score,
            "features": features
        })

    return jsonify({"processed": len(results), "results": results}), 200

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    data = request.json
    text = data.get('text', '')
    tags = data.get('tags', [])
    parent_id = data.get('parent_id')

    features = estimate_features(text)
    Q_score, _ = compute_Q(features)

    version = 1
    if parent_id:
        parent = PromptModel.query.get(parent_id)
        if parent:
            # Find the latest version in this lineage
            latest = PromptModel.query.filter_by(parent_id=parent_id).order_by(PromptModel.version.desc()).first()
            version = (latest.version if latest else parent.version) + 1

    prompt = PromptModel(
        text=text,
        q_score=Q_score,
        version=version,
        parent_id=parent_id
    )
    prompt.tags = tags
    prompt.features = features

    db.session.add(prompt)
    db.session.commit()

    return jsonify(prompt.to_dict()), 201

@app.route('/api/prompts/export', methods=['GET'])
def export_prompts():
    fmt = request.args.get('format', 'json')
    prompts = PromptModel.query.all()

    if fmt == 'csv':
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'version', 'Q_score', 'text', 'tags'])
        for p in prompts:
            writer.writerow([p.id, p.version, p.q_score, p.text, ','.join(p.tags)])
        return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=prompts.csv'}

    return jsonify([p.to_dict() for p in prompts])

@app.route('/api/prompts', methods=['GET'])
def list_prompts():
    prompts = PromptModel.query.order_by(PromptModel.created_at.desc()).all()
    return jsonify({
        "prompts": [p.to_dict() for p in prompts],
        "total": len(prompts),
        "page": 1,
        "per_page": 20,
        "pages": 1
    })

@app.route('/api/prompts/<int:id>', methods=['GET'])
def get_prompt(id: int):
    prompt = PromptModel.query.get(id)
    if prompt:
        return jsonify(prompt.to_dict())
    return jsonify({"error": "Prompt not found"}), 404

# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/prompts/<int:id>/analyze', methods=['POST'])
def analyze_prompt_by_id(id: int):
    prompt = get_prompt_or_404(id)
    features = estimate_features(prompt.text)
    Q_score, breakdown = compute_Q(features)

    return jsonify({
        "features": features,
        "Q_score": Q_score,
        "breakdown": breakdown,
        "level": get_quality_level(Q_score),
        "suggestions": suggest_improvements(features)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_prompt():
    data = request.json
    text = data.get('text', '')

    features = estimate_features(text)
    Q_score, breakdown = compute_Q(features)

    return jsonify({
        "features": features,
        "Q_score": Q_score,
        "breakdown": breakdown,
        "level": get_quality_level(Q_score),
        "suggestions": suggest_improvements(features)
    })

@app.route('/api/prompts/refine', methods=['POST'])
def refine_prompt_api():
    data = request.json
    text = data.get('text', '')

    features = estimate_features(text)
    Q, _ = compute_Q(features)

    # Identify weakest link
    weakest_dim = min(features.items(), key=lambda x: x[1])
    dim_key, score = weakest_dim

    dim_names = {
        'P': 'Persona',
        'T': 'Tone',
        'F': 'Format',
        'S': 'Specificity',
        'C': 'Constraints',
        'R': 'Context'
    }

    refinement_templates = {
        'P': "Add: 'You are an [Expert Role] with [X] years of experience in [Domain].'",
        'T': "Add: 'Use a [Formal/Technical/Academic] tone appropriate for [Audience].'",
        'F': "Add: 'Output should be in [JSON/Markdown/Table] format with the following structure: [Schema].'",
        'S': "Add: 'Ensure the output meets these metrics: [Latency/Accuracy/Count].'",
        'C': "Add: 'Constraints: Must include [X], Cannot use [Y], Validation rules: [Rules].'",
        'R': "Add: 'Context: This is for [Project/Use Case]. Background: [History]. Target Audience: [Audience].'"
    }

    suggestion = refinement_templates[dim_key]

    return jsonify({
        "original_q": Q,
        "weakest_dimension": dim_names[dim_key],
        "weakest_score": score,
        "suggestion": suggestion,
        "actionable_instruction": f"To improve your prompt's {dim_names[dim_key]} score from {score:.2f}, {suggestion.lower()}"
    })

# ============================================================================
# OPTIMIZATION ENDPOINTS
# ============================================================================

@app.route('/api/prompts/<int:id>/optimize', methods=['POST'])
def optimize_saved_prompt(id):
    prompt_obj = get_prompt_or_404(id)

    data = request.json or {}
    target_quality = data.get('target_quality', 0.85)
    strategy = data.get('strategy', 'balanced')
    estimate_only = data.get('estimate_only', False)

    if not (0.0 <= target_quality <= 1.0):
        return jsonify({"error": "target_quality must be between 0 and 1"}), 400

    if strategy not in ['balanced', 'cost_efficient', 'max_quality']:
        return jsonify({"error": "Invalid strategy"}), 400

    try:
        features = estimate_features(prompt_obj.text)
        current_q, _ = compute_Q(features)

        if estimate_only:
            estimate = estimate_optimization_cost(
                prompt=prompt_obj.text,
                current_q=current_q,
                target_q=target_quality,
                strategy=strategy
            )
            return jsonify(asdict(estimate) if hasattr(estimate, 'to_dict') is False else estimate.to_dict()), 200

        result = optimize_prompt(
            prompt=prompt_obj.text,
            target_quality=target_quality,
            strategy=strategy
        )

        if data.get('save_as_new', False):
            optimized = PromptModel(
                text=result.optimized_prompt,
                q_score=result.optimized_q,
                parent_id=id,
                version=prompt_obj.version + 1
            )
            optimized.tags = prompt_obj.tags + ['optimized']
            optimized.features = result.iterations[-1].features

            db.session.add(optimized)
            db.session.commit()

            return jsonify({
                **result.to_dict(),
                'saved_prompt_id': optimized.id
            }), 201

        return jsonify(result.to_dict()), 200

    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def optimize_ad_hoc():
    data = request.json
    prompt_text = data.get('text', '')
    if not prompt_text:
        return jsonify({"error": "Prompt text required"}), 400

    target_quality = data.get('target_quality', 0.85)
    strategy = data.get('strategy', 'balanced')

    try:
        result = optimize_prompt(
            prompt=prompt_text,
            target_quality=target_quality,
            strategy=strategy
        )
        return jsonify(result.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/optimize/estimate', methods=['POST'])
def estimate_optimization_endpoint():
    data = request.json
    prompt_text = data.get('text', '')
    if not prompt_text:
        return jsonify({"error": "Prompt text required"}), 400

    target_quality = data.get('target_quality', 0.85)
    strategy = data.get('strategy', 'balanced')

    try:
        features = estimate_features(prompt_text)
        current_q, _ = compute_Q(features)
        estimate = estimate_optimization_cost(
            prompt=prompt_text,
            current_q=current_q,
            target_q=target_quality,
            strategy=strategy
        )
        return jsonify(estimate.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/optimize/batch', methods=['POST'])
def optimize_batch():
    data = request.json
    prompts_data = data.get('prompts', [])
    strategy = data.get('strategy', 'balanced')

    results = []
    total_cost = 0
    successful = 0
    failed = 0

    for item in prompts_data:
        p_id = item.get('id')
        target_q = item.get('target_quality', 0.85)

        prompt_obj = PromptModel.query.get(p_id)
        if not prompt_obj:
            results.append({"prompt_id": p_id, "status": "failed", "error": "Not found"})
            failed += 1
            continue

        try:
            res = optimize_prompt(prompt_obj.text, target_quality=target_q, strategy=strategy)
            results.append({"prompt_id": p_id, "status": "success", "result": res.to_dict()})
            total_cost += res.total_cost_usd
            successful += 1
        except Exception as e:
            results.append({"prompt_id": p_id, "status": "failed", "error": str(e)})
            failed += 1

    return jsonify({
        "results": results,
        "total_cost": total_cost,
        "successful": successful,
        "failed": failed
    }), 200

# ============================================================================
# LLM GENERATION ENDPOINTS
# ============================================================================

@app.route('/api/prompts/<int:id>/generate', methods=['POST'])
def generate_for_prompt(id):
    prompt_obj = get_prompt_or_404(id)

    data = request.json or {}
    provider = data.get('provider', 'claude')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 2048)

    try:
        response = generate_response(
            prompt=prompt_obj.text,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            analyze_quality=True
        )

        return jsonify({
            "text": response.text,
            "provider": response.provider,
            "model": response.model,
            "tokens": {
                "input": response.prompt_tokens,
                "output": response.completion_tokens,
                "total": response.total_tokens
            },
            "cost_usd": response.total_cost_usd,
            "latency_ms": response.latency_ms,
            "quality": {
                "features": response.quality_features,
                "score": response.quality_score,
                "level": response.quality_level
            },
            "timestamp": response.timestamp.isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_live():
    data = request.json
    prompt = data.get('text', '')
    if not prompt:
        return jsonify({"error": "Prompt text required"}), 400

    provider = data.get('provider', 'claude')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 2048)

    try:
        response = generate_response(
            prompt=prompt,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            analyze_quality=True
        )
        return jsonify(response.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate/estimate', methods=['POST'])
def estimate_generation_cost_endpoint():
    data = request.json
    prompt = data.get('text', '')
    provider = data.get('provider', 'claude')
    max_tokens = data.get('max_tokens', 2048)

    try:
        cost_data = estimate_llm_cost(
            prompt=prompt,
            provider=provider,
            max_tokens=max_tokens
        )
        return jsonify(cost_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate/compare', methods=['POST'])
def compare_llm_providers_endpoint():
    data = request.json
    prompt = data.get('text', '')
    providers = data.get('providers', ['claude', 'openai'])

    try:
        results = compare_providers(
            prompt=prompt,
            providers=providers
        )
        output = {}
        for provider, response in results.items():
            if response:
                output[provider] = response.to_dict()
            else:
                output[provider] = {"error": "Generation failed"}
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<int:id>/variants', methods=['POST'])
def generate_variants(id):
    prompt = get_prompt_or_404(id)
    variant_texts = generate_variants_logic(prompt.text)
    variants = []

    for v in variant_texts:
        features = estimate_features(v['text'])
        q, _ = compute_Q(features)
        variants.append({
            "type": v['type'],
            "text": v['text'],
            "Q_score": q,
            "features": features
        })

    # Determine winner based on Q_score
    winner = max(variants, key=lambda x: x['Q_score'])['type']

    return jsonify({"variants": variants, "comparison": {"winner": winner}}), 201

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Bolt ⚡: Optimized analytics using DB-level aggregation"""
    stats = db.session.query(
        func.avg(PromptModel.q_score),
        func.count(PromptModel.id)
    ).first()

    avg_q = stats[0] or 0
    count = stats[1] or 0

    if count == 0:
        return jsonify({"avg_q": 0, "count": 0})

    distribution = {
        "Excellent": PromptModel.query.filter(PromptModel.q_score >= 0.9).count(),
        "Good": PromptModel.query.filter(PromptModel.q_score >= 0.8, PromptModel.q_score < 0.9).count(),
        "Fair": PromptModel.query.filter(PromptModel.q_score >= 0.7, PromptModel.q_score < 0.8).count(),
        "Poor": PromptModel.query.filter(PromptModel.q_score < 0.7).count()
    }

    return jsonify({
        "avg_q": round(avg_q, 4),
        "count": count,
        "distribution": distribution
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
