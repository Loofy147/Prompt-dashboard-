from typing import Dict
import re

# Pre-compiled DIGIT regex (faster than character loop)
DIGIT_RE = re.compile(r"\d")

def estimate_features(t: str) -> Dict[str, float]:
    """
    Bolt ⚡: State-of-the-art high-performance feature extraction.
    Uses Boyer-Moore string searching (via 'in' operator) and minimal allocations.
    """
    if not t:
        return {'P': 0.0, 'T': 0.0, 'F': 0.0, 'S': 0.0, 'C': 0.0, 'R': 0.0}

    low_t = t.lower()
    t_len = len(t)

    # P (Persona) - Weight: 0.18
    p_score = 0.4
    if "you are" in low_t or "expert" in low_t or "persona" in low_t:
        p_score = 0.8
        if "years of experience" in low_t or "senior" in low_t or "specialist" in low_t or "architect" in low_t or "principal" in low_t:
            p_score = 0.95

    # T (Tone) - Weight: 0.22
    t_score = 0.5
    if any(tk in low_t for tk in ("formal", "casual", "professional", "technical", "academic", "persuasive", "friendly", "neutral", "authoritative")):
        t_score = 0.85
    if "tone" in low_t or "voice" in low_t:
        t_score = 0.95

    # F (Format) - Weight: 0.20
    f_score = 0.3
    if any(fk in low_t for fk in ("json", "markdown", "table", "csv", "bullet points", "list", "xml", "latex", "structure", "schema")):
        f_score = 0.7
    if any(fk in low_t for fk in ("format", "output", "sections", "headers", "subheaders")):
        f_score = 0.95

    # S (Specificity) - Weight: 0.18
    s_score = 0.4
    if DIGIT_RE.search(low_t):
        s_score = 0.7
    if any(m in low_t for m in ("latency", "throughput", "availability", "budget", "count", "words", "characters", "limit", "target", "metric")):
        s_score = 0.9

    # C (Constraints) - Weight: 0.12
    c_score = 0.3
    if any(ck in low_t for ck in ("must", "cannot", "don't", "avoid", "ensure", "always", "never", "constraint", "limit", "hard limit")):
        c_score = 0.8
    if any(ck in low_t for ck in ("validation", "rules", "enforce", "check", "verify")):
        c_score = 0.95

    # R (Context) - Weight: 0.10
    r_score = 0.3
    if t_len > 1000:
        r_score = 0.9
    elif t_len > 500:
        r_score = 0.8
    elif t_len > 200:
        r_score = 0.6

    if any(rk in low_t for rk in ("background", "audience", "context", "history", "use case", "scenario", "mission")):
        r_score = 0.95

    return {
        'P': round(p_score, 2),
        'T': round(t_score, 2),
        'F': round(f_score, 2),
        'S': round(s_score, 2),
        'C': round(c_score, 2),
        'R': round(r_score, 2)
    }
