from typing import Dict
import re

# Pre-compiled regex patterns for high-performance matching
DIGIT_RE = re.compile(r"\d")
PERSONA_RE = re.compile(r"you are|expert|persona")
PERSONA_ADV_RE = re.compile(r"years of experience|senior|specialist|architect|principal")
TONE_RE = re.compile(r"formal|casual|professional|technical|academic|persuasive|friendly|neutral|authoritative")
TONE_ADV_RE = re.compile(r"tone|voice")
FORMAT_RE = re.compile(r"json|markdown|table|csv|bullet points|list|xml|latex|structure|schema")
FORMAT_ADV_RE = re.compile(r"format|output|sections|headers|subheaders")
SPECIFICITY_RE = re.compile(r"latency|throughput|availability|budget|count|words|characters|limit|target|metric")
CONSTRAINTS_RE = re.compile(r"must|cannot|don't|avoid|ensure|always|never|constraint|limit|hard limit")
CONSTRAINTS_ADV_RE = re.compile(r"validation|rules|enforce|check|verify")
CONTEXT_RE = re.compile(r"background|audience|context|history|use case|scenario|mission")

def estimate_features(t: str) -> Dict[str, float]:
    """
    Bolt ⚡: State-of-the-art high-performance feature extraction.
    Uses pre-compiled regex and minimal allocations to achieve sub-15ms analysis.
    """
    if not t:
        return {'P': 0.0, 'T': 0.0, 'F': 0.0, 'S': 0.0, 'C': 0.0, 'R': 0.0}

    low_t = t.lower()
    t_len = len(t)

    # P (Persona) - Weight: 0.20
    p_score = 0.4
    if PERSONA_RE.search(low_t):
        p_score = 0.8
        if PERSONA_ADV_RE.search(low_t):
            p_score = 0.95

    # T (Tone) - Weight: 0.18
    t_score = 0.5
    if TONE_RE.search(low_t):
        t_score = 0.85
    if TONE_ADV_RE.search(low_t):
        t_score = 0.95

    # F (Format) - Weight: 0.18
    f_score = 0.3
    if FORMAT_RE.search(low_t):
        f_score = 0.7
    if FORMAT_ADV_RE.search(low_t):
        f_score = 0.95

    # S (Specificity) - Weight: 0.18
    s_score = 0.4
    if DIGIT_RE.search(low_t):
        s_score = 0.7
    if SPECIFICITY_RE.search(low_t):
        s_score = 0.9

    # C (Constraints) - Weight: 0.13
    c_score = 0.3
    if CONSTRAINTS_RE.search(low_t):
        c_score = 0.8
    if CONSTRAINTS_ADV_RE.search(low_t):
        c_score = 0.95

    # R (Context) - Weight: 0.13
    r_score = 0.3
    if t_len > 1000:
        r_score = 0.9
    elif t_len > 500:
        r_score = 0.8
    elif t_len > 200:
        r_score = 0.6

    if CONTEXT_RE.search(low_t):
        r_score = 0.95

    return {
        'P': round(p_score, 2),
        'T': round(t_score, 2),
        'F': round(f_score, 2),
        'S': round(s_score, 2),
        'C': round(c_score, 2),
        'R': round(r_score, 2)
    }
