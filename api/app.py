from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from quality_calculator import compute_Q, suggest_improvements, get_quality_level
from feature_analyzer import estimate_features
from variant_generator import generate_variants_logic
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
    q_score = db.Column(db.Float, nullable=False)
    features_json = db.Column(db.Text, nullable=False)
    version = db.Column(db.Integer, default=1)
    parent_id = db.Column(db.Integer, db.ForeignKey('prompt_model.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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
def get_prompt(id):
    prompt = PromptModel.query.get(id)
    if prompt:
        return jsonify(prompt.to_dict())
    return jsonify({"error": "Prompt not found"}), 404

@app.route('/api/prompts/<int:id>/analyze', methods=['POST'])
def analyze_prompt_by_id(id):
    prompt = PromptModel.query.get(id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    features = estimate_features(prompt.text)
    Q_score, breakdown = compute_Q(features)

    return jsonify({
        "features": features,
        "Q_score": Q_score,
        "breakdown": breakdown,
        "level": get_quality_level(Q_score),
        "suggestions": suggest_improvements(features)
    })

@app.route('/api/prompts/<int:id>/variants', methods=['POST'])
def generate_variants(id):
    prompt = PromptModel.query.get(id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

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
    prompts = PromptModel.query.all()
    if not prompts:
        return jsonify({"avg_q": 0, "count": 0})

    avg_q = sum(p.q_score for p in prompts) / len(prompts)
    return jsonify({
        "avg_q": round(avg_q, 4),
        "count": len(prompts),
        "distribution": {
            "Excellent": len([p for p in prompts if p.q_score >= 0.9]),
            "Good": len([p for p in prompts if 0.8 <= p.q_score < 0.9]),
            "Fair": len([p for p in prompts if 0.7 <= p.q_score < 0.8]),
            "Poor": len([p for p in prompts if p.q_score < 0.7])
        }
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
