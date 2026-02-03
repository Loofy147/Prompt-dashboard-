import time
import json
import datetime
from app import app, db, PromptModel

def run_benchmark(n=1000):
    with app.app_context():
        # Create n mock prompts
        prompts = []
        now = datetime.datetime.utcnow()
        for i in range(n):
            p = PromptModel(
                text=f"Prompt {i}",
                q_score=0.85,
                features_json='{"P": 0.8, "T": 0.8, "F": 0.8, "S": 0.8, "C": 0.8, "R": 0.8}',
                tags_json='["tag1", "tag2"]'
            )
            p.created_at = now
            prompts.append(p)

        start = time.perf_counter()
        # Optimized loop (excluding features)
        for _ in range(10):
            [ {
                "id": p.id,
                "text": p.text,
                "tags": json.loads(p.tags_json),
                "Q_score": p.q_score,
                "version": p.version,
                "parent_id": p.parent_id,
                "created_at": p.created_at.isoformat()
            } for p in prompts ]
        end = time.perf_counter()

        total_time_ms = (end - start) * 1000 / 10
        avg_ms = total_time_ms / n
        print(f"Average optimized serialization execution time: {avg_ms:.4f} ms")
        print(f"Total time for {n} prompts: {total_time_ms:.2f} ms")
        return avg_ms

if __name__ == "__main__":
    run_benchmark()
