from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from quality_calculator import compute_Q, suggest_improvements, get_quality_level
from feature_analyzer import estimate_features
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

    features = estimate_features(text)
    Q_score, _ = compute_Q(features)

    prompt = PromptModel(
        text=text,
        q_score=Q_score
    )
    prompt.tags = tags
    prompt.features = features

    db.session.add(prompt)
    db.session.commit()

    return jsonify(prompt.to_dict()), 201

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

    # Mock variant generation
    variants = [
        {"type": "concise", "text": f"Concise: {prompt.text[:50]}...", "Q_score": 0.75},
        {"type": "neutral", "text": f"Neutral: {prompt.text}", "Q_score": 0.82},
        {"type": "commanding", "text": f"Commanding: DO {prompt.text}", "Q_score": 0.88}
    ]
    return jsonify({"variants": variants, "comparison": {"winner": "commanding"}}), 201

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
