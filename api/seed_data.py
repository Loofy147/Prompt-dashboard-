import requests
import json

BASE_URL = "http://localhost:5000/api"

seeds = [
    {
        "text": "You are a Senior Systems Architect. Design a scalable microservices architecture for a global e-commerce platform using Kubernetes and Kafka. Output should be a detailed Markdown document with 5 sections: Overview, Schema, Data Flow, Security, and Scalability. Constraints: latency < 200ms, 99.99% availability.",
        "tags": ["technical", "architecture"]
    },
    {
        "text": "Write a cool story about a cat.",
        "tags": ["creative"]
    },
    {
        "text": "You are an Academic Researcher. Synthesize the findings of the provided 10 papers on climate change mitigation. Provide a formal report in LaTeX format, citing all sources using APA style. Focus on carbon sequestration metrics and policy recommendations.",
        "tags": ["research", "academic"]
    },
    {
        "text": "Write a marketing email for a new SaaS product called 'PromptMaster'. Use a professional but persuasive tone. Target audience is CTOs of mid-sized tech companies. Mention features like real-time quality analysis and A/B testing.",
        "tags": ["marketing", "b2b"]
    },
    {
        "text": "Create a product brief for a new mobile app that helps people track their plants. Include user personas, core features, and a 6-month roadmap. Use a structured template.",
        "tags": ["product", "brief"]
    }
]

def seed():
    for seed in seeds:
        try:
            response = requests.post(f"{BASE_URL}/prompts", json=seed)
            if response.status_code == 201:
                data = response.json()
                print(f"Created prompt {data['id']}: Q={data['Q_score']:.2f}")
            else:
                print(f"Failed to create prompt: {response.text}")
        except Exception as e:
            print(f"Error connecting to backend: {e}")

if __name__ == "__main__":
    seed()
