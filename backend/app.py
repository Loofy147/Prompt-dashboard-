from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from quality_calculator import compute_Q, suggest_improvements, get_quality_level
import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
db_path = os.path.join(os.path.dirname(__file__), 'prompts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

def estimate_features(t):
    low_t = t.lower()

    # P (Persona)
    p_score = 0.4
    if "you are" in low_t or "expert" in low_t or "persona" in low_t:
        p_score = 0.8
        if "years of experience" in low_t or "senior" in low_t or "specialist" in low_t:
            p_score = 0.95

    # T (Tone)
    t_score = 0.5
    tone_keywords = ["formal", "casual", "professional", "technical", "academic", "persuasive", "friendly", "neutral"]
    if any(tk in low_t for tk in tone_keywords):
        t_score = 0.85
    if "tone" in low_t or "voice" in low_t:
        t_score = 0.95

    # F (Format)
    f_score = 0.3
    format_keywords = ["json", "markdown", "table", "csv", "bullet points", "list", "xml", "latex", "structure"]
    if any(fk in low_t for fk in format_keywords):
        f_score = 0.7
    if "format" in low_t or "output" in low_t or "sections" in low_t or "schema" in low_t:
        f_score = 0.95

    # S (Specificity)
    s_score = 0.4
    if any(c.isdigit() for c in low_t):
        s_score = 0.7
    metrics = ["latency", "throughput", "availability", "budget", "count", "words", "characters", "limit"]
    if any(m in low_t for m in metrics):
        s_score = 0.9

    # C (Constraints)
    c_score = 0.3
    constraint_keywords = ["must", "cannot", "don't", "avoid", "ensure", "always", "never", "constraint", "limit"]
    if any(ck in low_t for ck in constraint_keywords):
        c_score = 0.8
    if "validation" in low_t or "rules" in low_t or "enforce" in low_t:
        c_score = 0.95

    # R (Context)
    r_score = 0.3
    if len(t) > 200:
        r_score = 0.6
    if len(t) > 500:
        r_score = 0.8
    context_keywords = ["background", "audience", "context", "history", "use case", "scenario"]
    if any(rk in low_t for rk in context_keywords):
        r_score = 0.95

    return {'P': p_score, 'T': t_score, 'F': f_score, 'S': s_score, 'C': c_score, 'R': r_score}

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
