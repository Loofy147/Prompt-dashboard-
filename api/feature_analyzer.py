import re
"""
NLP-based feature extraction for prompts.
Optimized with type hints and efficient keyword matching.
"""
from typing import Dict

def estimate_features(t: str) -> Dict[str, float]:
    """
    Analyzes prompt text to estimate PES dimension scores (0.0 - 1.0).

    Args:
        t: The prompt text to analyze.

    Returns:
        A dictionary mapping dimension keys (P, T, F, S, C, R) to scores.
    """
    if not t:
        return {'P': 0.0, 'T': 0.0, 'F': 0.0, 'S': 0.0, 'C': 0.0, 'R': 0.0}

    low_t = t.lower()
    t_len = len(t)

    # P (Persona) - Weight: 0.18
    p_score = 0.4
    if "you are" in low_t or "expert" in low_t or "persona" in low_t:
        p_score = 0.8
        if any(w in low_t for w in ["years of experience", "senior", "specialist", "architect", "principal"]):
            p_score = 0.95

    # T (Tone) - Weight: 0.22
    t_score = 0.5
    tone_keywords = ["formal", "casual", "professional", "technical", "academic", "persuasive", "friendly", "neutral", "authoritative"]
    if any(tk in low_t for tk in tone_keywords):
        t_score = 0.85
    if "tone" in low_t or "voice" in low_t:
        t_score = 0.95

    # F (Format) - Weight: 0.20
    f_score = 0.3
    format_keywords = ["json", "markdown", "table", "csv", "bullet points", "list", "xml", "latex", "structure", "schema"]
    if any(fk in low_t for fk in format_keywords):
        f_score = 0.7
    if any(fk in low_t for fk in ["format", "output", "sections", "headers", "subheaders"]):
        f_score = 0.95

    # S (Specificity) - Weight: 0.18
    s_score = 0.4
    if re.search(r'\d', low_t):
        s_score = 0.7
    metrics = ["latency", "throughput", "availability", "budget", "count", "words", "characters", "limit", "target", "metric"]
    if any(m in low_t for m in metrics):
        s_score = 0.9

    # C (Constraints) - Weight: 0.12
    c_score = 0.3
    constraint_keywords = ["must", "cannot", "don't", "avoid", "ensure", "always", "never", "constraint", "limit", "hard limit"]
    if any(ck in low_t for ck in constraint_keywords):
        c_score = 0.8
    if any(ck in low_t for ck in ["validation", "rules", "enforce", "check", "verify"]):
        c_score = 0.95

    # R (Context) - Weight: 0.10
    r_score = 0.3
    if t_len > 200:
        r_score = 0.6
    if t_len > 500:
        r_score = 0.8
    if t_len > 1000:
        r_score = 0.9
    context_keywords = ["background", "audience", "context", "history", "use case", "scenario", "mission"]
    if any(rk in low_t for rk in context_keywords):
        r_score = 0.95

    return {
        'P': round(p_score, 2),
        'T': round(t_score, 2),
        'F': round(f_score, 2),
        'S': round(s_score, 2),
        'C': round(c_score, 2),
        'R': round(r_score, 2)
    }
