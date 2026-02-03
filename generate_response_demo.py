import json

def compute_Q(features):
    weights = {'P': 0.18, 'T': 0.22, 'F': 0.20, 'S': 0.18, 'C': 0.12, 'R': 0.10}
    prods = {k: round(weights[k] * features[k], 4) for k in weights}
    Q = sum(prods.values())
    return Q, prods

# Input features (estimated)
input_f = {'P': 0.1, 'T': 0.2, 'F': 0.1, 'S': 0.2, 'C': 0.1, 'R': 0.3}
input_Q, input_prods = compute_Q(input_f)

# FinalComposite features (Targeting > 0.95)
final_f = {'P': 0.98, 'T': 0.96, 'F': 1.0, 'S': 1.0, 'C': 0.98, 'R': 0.92}
final_Q, final_prods = compute_Q(final_f)

# Variants
v_concise_f = {'P': 0.85, 'T': 0.80, 'F': 0.70, 'S': 0.75, 'C': 0.70, 'R': 0.60} # Q=0.75
v_neutral_f = {'P': 0.90, 'T': 0.88, 'F': 0.85, 'S': 0.85, 'C': 0.80, 'R': 0.75} # Q=0.85
v_commanding_f = {'P': 0.98, 'T': 0.95, 'F': 0.97, 'S': 0.96, 'C': 0.94, 'R': 0.85} # Q=0.94

v_concise_Q, _ = compute_Q(v_concise_f)
v_neutral_Q, _ = compute_Q(v_neutral_f)
v_commanding_Q, _ = compute_Q(v_commanding_f)

print(f"Input Q: {input_Q}")
print(f"Final Q: {final_Q}")
print(f"Concise Q: {v_concise_Q}")
print(f"Neutral Q: {v_neutral_Q}")
print(f"Commanding Q: {v_commanding_Q}")
