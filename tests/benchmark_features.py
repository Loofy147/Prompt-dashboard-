import time
from feature_analyzer import estimate_features

def run_benchmark(n=1000):
    test_text = """
    You are an expert principal architect with 20 years of experience.
    Please provide a technical specification in JSON format.
    The response must have a latency under 200ms and 99.9% availability.
    Ensure all validation rules are enforced.
    Background: This is for a high-traffic fintech application.
    """ * 10  # ~2000 chars

    start = time.perf_counter()
    for _ in range(n):
        estimate_features(test_text)
    end = time.perf_counter()

    avg_ms = ((end - start) / n) * 1000
    print(f"Average execution time: {avg_ms:.4f} ms")
    return avg_ms

if __name__ == "__main__":
    run_benchmark()
