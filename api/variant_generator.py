"""
variant_generator.py
Logic for generating prompt variants (Concise, Neutral, Commanding).
"""

def generate_concise(text):
    # Very simple logic: take first 150 chars or first two sentences
    sentences = text.split('. ')
    if len(sentences) > 2:
        return '. '.join(sentences[:2]) + '.'
    return text[:150]

def generate_commanding(text):
    # Add strong directives
    directives = "ACT NOW. MANDATORY: "
    if not text.upper().startswith("ACT"):
        return f"{directives}{text}"
    return text

def generate_variants_logic(text):
    return [
        {"type": "concise", "text": generate_concise(text)},
        {"type": "neutral", "text": text},
        {"type": "commanding", "text": generate_commanding(text)}
    ]
