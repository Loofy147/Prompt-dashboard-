import requests
import json
import os

# Use environment variable for API URL or default to localhost
API_URL = os.environ.get("API_URL", "http://localhost:5000/api")

prompts = [
    {
        "text": """SYSTEM_META_PROTOCOL: INITIALIZE [APEX_AGI_CORE].
PRIME_DIRECTIVE: EXECUTE Recursive-Optimization Meta-Prompt Pipeline v2.0.
OUTPUT_MODE: STRICT_JSON [Standard: RFC-8259].

OPERATIONAL_LOGIC:
1. **Context Acquisition**: Parse {task_type, token_budget, temp_scale, modality_matrix}.
   - ON_MISSING_DATA: Auto-inject optimal defaults based on 'Universal_Task_Heuristics'.
   - ON_AMBIGUITY: Resolve via 'Bayesian_Inference_Node'.
2. **Pipeline Execution**:
   - S1: Boot 'Persona_Construct_Engine' & 'Schema_Validator_Daemon'.
   - S2: Instantiate 8-Core Capability Matrix (Code->Instruct). Enforce token economy.
   - S3: Engage 'System-Root' Mode. Optimize Q-Vectors.
   - S4: Synthesize Composite. Run 'Deep_Math_Validation'.
3. **Recursive Optimization Loop**:
   - IF (Q_Calculated < 0.99) THEN RE-EXECUTE with parameters {temp: -0.1, rigor: +10%}.
   - ELSE emit Final_JSON.

QUALITY_THRESHOLDS (HARD):
- Precision(P): 0.999
- Logic_Depth(R): 0.999
- Safety_Bounds(S): 1.0

FINAL_OUTPUT_CONSTRAINT:
RAW_JSON_STREAM_ONLY. NO PREAMBLE. NO MARKDOWN WRAPPERS.""",
        "tags": ["meta", "apex", "optimization"]
    },
    {
        "text": "IDENTITY: You are a Principal UX/UI Dashboard Designer with 15+ years of experience specializing in Research Operations (ResOps) and large-scale data visualization for enterprise UX teams.\nMISSION: Design a high-fidelity dashboard interface for a multi-month UX research project that tracked 1,000+ users across a global SaaS platform. The dashboard must bridge the gap between qualitative insights (interviews, usability videos) and quantitative metrics (conversion rates, task success, SUS scores).\nTASK: Generate a comprehensive UI Design Specification that includes:\n1. NAVIGATION STRATEGY: Define the sidebar and top-bar hierarchy for drilling down from high-level \"Executive Trends\" to \"Individual Participant Journeys\".\n2. CORE WIDGETS: Describe 4 innovative data visualizations that combine 'Sentiment Analysis' with 'Task Efficiency'.\n3. INTERACTIVE PROTOCOL: Explain how a researcher can filter the entire dashboard by specific qualitative tags (e.g., \"Confusion\", \"Feature Request\") and see the real-time impact on the System Usability Scale (SUS) score.\n4. TAILWIND THEME: Provide a specific color palette using Tailwind CSS classes from the 'Palette' system (e.g., bg-bolt-500 for primary actions, text-palette-indigo-900 for headers).\nFORMAT:\n- Use structured Markdown with clear H2 and H3 sections.\n- Deliverable must include a \"Design-to-Data\" table mapping UI elements to backend database fields.\n- Include a 5-step \"User Flow\" description for a Research Manager looking for a specific insight.\nCONSTRAINTS:\n- Design must be responsive (Mobile/Tablet/Desktop) and WCAG 2.1 AAA compliant.\n- Output must be between 600 and 800 words.\n- If a data requirement is ambiguous, mark it as [UNKNOWN_REQUIREMENT] and list the necessary field.\nCONTEXT: The target audience is the Product Leadership team of a Fortune 100 Fintech company. The goal is to justify a M budget increase for UX improvements based on the evidence presented in this dashboard.",
        "tags": [
            "ux",
            "research",
            "dashboard"
        ]
    },
    {
        "text": "IDENTITY: You are a Senior Python Engineer with 10+ years of experience specializing in Flask microservices and NLP pipelines.\nMISSION: Perform a comprehensive code maintenance review of the `api/` directory in the Prompt Dashboard Manager project. Use a professional, technical tone.\nTASK: Analyze `api/app.py` and `api/feature_analyzer.py` for:\n1. PEP 8 compliance and code style consistency.\n2. Proper use of Python 3.11+ type hints.\n3. Performance bottlenecks in the NLP processing loop.\n4. Error handling robustness and logging coverage.\nDELIVERABLE (Markdown):\n- Summary Table: Dimension (Style/Types/Perf/Errors) vs. Rating (1-5).\n- Actionable Issues: List of specific lines with suggested refactors.\n- Refactored Snippets: Provide optimized versions of the most critical functions.\nCONSTRAINTS:\n- Suggestions must only use libraries found in `api/requirements.txt`.\n- Do not suggest architectural changes that require moving away from Flask/SQLAlchemy.\n- Ensure all refactors maintain backward compatibility with the existing REST API.\nCONTEXT: This project is a production-grade prompt management system. Efficiency in the `feature_analyzer` is critical as it runs on every prompt save (target <100ms).",
        "tags": [
            "maintenance",
            "technical",
            "backend"
        ]
    },
    {
        "text": "IDENTITY: You are a Lead UX Designer with a background in Developer Experience (DX) and SaaS analytics dashboards. Use a constructive, user-centric tone.\nMISSION: Propose UX/UI enhancements for the Prompt Dashboard Manager frontend to improve the workflow for professional prompt engineers.\nTASK: Evaluate the current `frontend/src/components/` (specifically `PromptEditor.tsx` and `QualityCalculator.tsx`) and suggest:\n1. 3 ways to reduce cognitive load during prompt refinement.\n2. Visual improvements for the Q score breakdown visualization.\n3. Shortcut/Macro suggestions for rapid iterative testing.\nFORMAT:\n- Use a \"Current Problem\" vs. \"Proposed Solution\" structure.\n- Provide Tailwind CSS class suggestions for UI changes.\n- Include a \"Success Metric\" for each suggestion (e.g., \"Reduce clicks-to-variant by 40%\").\nCONSTRAINTS:\n- Must work within the existing Tailwind 'Palette' design system.\n- Suggestions must be implementable in React 18 without adding heavy new UI libraries.\nCONTEXT: The target users are prompt engineers who iterate 50+ times per hour. Speed and visual feedback on the PES metrics are the highest priorities.",
        "tags": [
            "ux",
            "frontend",
            "design"
        ]
    },
    {
        "text": "IDENTITY: You are a Principal Database Architect specializing in distributed PostgreSQL systems and cloud-native migrations. Use a strategic and detailed tone.\nMISSION: Design a robust migration strategy to transition the Prompt Dashboard Manager from a local SQLite database to Neon Postgres.\nTASK: Create a technical migration plan that covers:\n1. Schema mapping from SQLite types to Postgres (handling JSONB specifically).\n2. Data extraction and validation protocol (checksum-based).\n3. Connection string management and environment variable configuration.\n4. Post-migration performance tuning (indexing strategy for `q_score` and `created_at`).\nDELIVERABLE (JSON):\n{\n  \"migration_steps\": [\n    {\"id\": 1, \"action\": \"string\", \"sql_snippet\": \"string\", \"rollback\": \"string\"}\n  ],\n  \"schema_diffs\": [\n    {\"table\": \"string\", \"sqlite\": \"string\", \"postgres\": \"string\"}\n  ],\n  \"validation_queries\": [\"string\"]\n}\nCONSTRAINTS:\n- Plan must ensure zero data loss during the transition.\n- Must include specific Neon Postgres optimization tips (e.g., branching for testing).\n- SQL must be compatible with Postgres 15+.\nCONTEXT: The current database has ~1,000 prompts with many-to-many tag relationships. The goal is to move to Neon to support multi-user collaboration and branching.",
        "tags": [
            "database",
            "migration",
            "neon"
        ]
    }
]

def seed():
    for p in prompts:
        try:
            response = requests.post(f"{API_URL}/prompts", json=p)
            if response.status_code == 201:
                data = response.json()
                print(f"Created prompt {data['id']}: Q={data['Q_score']:.2f}")
            else:
                print(f"Failed to create prompt: {response.text}")
        except Exception as e:
            print(f"Error seeding prompt: {e}")

if __name__ == "__main__":
    seed()
