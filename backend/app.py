from flask import Flask, request, jsonify
from flask_cors import CORS
from quality_calculator import compute_Q, suggest_improvements, get_quality_level
import datetime

app = Flask(__name__)
CORS(app)

# Mock database
prompts = []
next_id = 1

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

def estimate_features(t):
    t = t.lower()
    p = 0.9 if "you are" in t or "expert" in t else 0.5
    tone = 0.8 if "please" not in t else 0.6 # Formal
    f = 0.9 if "format" in t or "json" in t or "markdown" in t or "output" in t else 0.4
    s = 0.8 if any(c.isdigit() for c in t) or "constraint" in t or "latency" in t else 0.5
    c = 0.7 if "must" in t or "not" in t or "limit" in t or "constraint" in t else 0.4
    r = 0.6 if len(t) > 200 else 0.3
    return {'P': p, 'T': tone, 'F': f, 'S': s, 'C': c, 'R': r}

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    global next_id
    data = request.json
    text = data.get('text', '')
    tags = data.get('tags', [])

    features = estimate_features(text)
    Q_score, breakdown = compute_Q(features)

    prompt = {
        "id": next_id,
        "text": text,
        "tags": tags,
        "Q_score": Q_score,
        "features": features,
        "created_at": datetime.datetime.now().isoformat()
    }
    prompts.append(prompt)
    next_id += 1
    return jsonify(prompt), 201

@app.route('/api/prompts', methods=['GET'])
def list_prompts():
    return jsonify({
        "prompts": prompts,
        "total": len(prompts),
        "page": 1,
        "per_page": 20,
        "pages": 1
    })

@app.route('/api/prompts/<int:id>', methods=['GET'])
def get_prompt(id):
    prompt = next((p for p in prompts if p['id'] == id), None)
    if prompt:
        return jsonify(prompt)
    return jsonify({"error": "Prompt not found"}), 404

@app.route('/api/prompts/<int:id>/analyze', methods=['POST'])
def analyze_prompt_by_id(id):
    prompt = next((p for p in prompts if p['id'] == id), None)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    features = estimate_features(prompt['text'])
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
    prompt = next((p for p in prompts if p['id'] == id), None)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    # Mock variant generation
    variants = [
        {"type": "concise", "text": f"Concise: {prompt['text'][:50]}...", "Q_score": 0.75},
        {"type": "neutral", "text": f"Neutral: {prompt['text']}", "Q_score": 0.82},
        {"type": "commanding", "text": f"Commanding: DO {prompt['text']}", "Q_score": 0.88}
    ]
    return jsonify({"variants": variants, "comparison": {"winner": "commanding"}}), 201

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    if not prompts:
        return jsonify({"avg_q": 0, "count": 0})

    avg_q = sum(p['Q_score'] for p in prompts) / len(prompts)
    return jsonify({
        "avg_q": round(avg_q, 4),
        "count": len(prompts),
        "distribution": {
            "Excellent": len([p for p in prompts if p['Q_score'] >= 0.9]),
            "Good": len([p for p in prompts if 0.8 <= p['Q_score'] < 0.9]),
            "Fair": len([p for p in prompts if 0.7 <= p['Q_score'] < 0.8]),
            "Poor": len([p for p in prompts if p['Q_score'] < 0.7])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
