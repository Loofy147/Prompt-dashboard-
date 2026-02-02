"""
feature_analyzer.py
NLP-based feature extraction for prompts.
"""

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
