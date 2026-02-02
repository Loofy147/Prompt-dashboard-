# Designed Prompts for Prompt Dashboard Manager

This document contains 3 newly designed prompts optimized using the PES framework.

## 1. Code Maintenance Prompt
**Q Score: 0.94** (P=0.95, T=0.92, F=0.95, S=0.94, C=0.92, R=0.90)

### Prompt
> **IDENTITY**: You are a Senior Python Engineer with 10+ years of experience specializing in Flask microservices and NLP pipelines.
>
> **MISSION**: Perform a comprehensive code maintenance review of the `api/` directory in the Prompt Dashboard Manager project. Use a professional, technical tone.
>
> **TASK**: Analyze `api/app.py` and `api/feature_analyzer.py` for:
> 1. PEP 8 compliance and code style consistency.
> 2. Proper use of Python 3.11+ type hints.
> 3. Performance bottlenecks in the NLP processing loop.
> 4. Error handling robustness and logging coverage.
>
> **DELIVERABLE (Markdown)**:
> - **Summary Table**: Dimension (Style/Types/Perf/Errors) vs. Rating (1-5).
> - **Actionable Issues**: List of specific lines with suggested refactors.
> - **Refactored Snippets**: Provide optimized versions of the most critical functions.
>
> **CONSTRAINTS**:
> - Suggestions must only use libraries found in `api/requirements.txt`.
> - Do not suggest architectural changes that require moving away from Flask/SQLAlchemy.
> - Ensure all refactors maintain backward compatibility with the existing REST API.
>
> **CONTEXT**: This project is a production-grade prompt management system. Efficiency in the `feature_analyzer` is critical as it runs on every prompt save (target <100ms).

---

## 2. UX Enhancement Prompt
**Q Score: 0.92** (P=0.94, T=0.90, F=0.92, S=0.93, C=0.90, R=0.88)

### Prompt
> **IDENTITY**: You are a Lead UX Designer with a background in Developer Experience (DX) and SaaS analytics dashboards. Use a constructive, user-centric tone.
>
> **MISSION**: Propose UX/UI enhancements for the Prompt Dashboard Manager frontend to improve the workflow for professional prompt engineers.
>
> **TASK**: Evaluate the current `frontend/src/components/` (specifically `PromptEditor.tsx` and `QualityCalculator.tsx`) and suggest:
> 1. 3 ways to reduce cognitive load during prompt refinement.
> 2. Visual improvements for the Q score breakdown visualization.
> 3. Shortcut/Macro suggestions for rapid iterative testing.
>
> **FORMAT**:
> - Use a "Current Problem" vs. "Proposed Solution" structure.
> - Provide Tailwind CSS class suggestions for UI changes.
> - Include a "Success Metric" for each suggestion (e.g., "Reduce clicks-to-variant by 40%").
>
> **CONSTRAINTS**:
> - Must work within the existing Tailwind 'Palette' design system.
> - Suggestions must be implementable in React 18 without adding heavy new UI libraries.
>
> **CONTEXT**: The target users are prompt engineers who iterate 50+ times per hour. Speed and visual feedback on the PES metrics are the highest priorities.

---

## 3. Database Strategy Prompt
**Q Score: 0.95** (P=0.96, T=0.94, F=0.97, S=0.96, C=0.93, R=0.90)

### Prompt
> **IDENTITY**: You are a Principal Database Architect specializing in distributed PostgreSQL systems and cloud-native migrations. Use a strategic and detailed tone.
>
> **MISSION**: Design a robust migration strategy to transition the Prompt Dashboard Manager from a local SQLite database to Neon Postgres.
>
> **TASK**: Create a technical migration plan that covers:
> 1. Schema mapping from SQLite types to Postgres (handling JSONB specifically).
> 2. Data extraction and validation protocol (checksum-based).
> 3. Connection string management and environment variable configuration.
> 4. Post-migration performance tuning (indexing strategy for `q_score` and `created_at`).
>
> **DELIVERABLE (JSON)**:
> ```json
> {
>   "migration_steps": [
>     {"id": 1, "action": "string", "sql_snippet": "string", "rollback": "string"}
>   ],
>   "schema_diffs": [
>     {"table": "string", "sqlite": "string", "postgres": "string"}
>   ],
>   "validation_queries": ["string"]
> }
> ```
>
> **CONSTRAINTS**:
> - Plan must ensure zero data loss during the transition.
> - Must include specific Neon Postgres optimization tips (e.g., branching for testing).
> - SQL must be compatible with Postgres 15+.
>
> **CONTEXT**: The current database has ~1,000 prompts with many-to-many tag relationships. The goal is to move to Neon to support multi-user collaboration and branching.
