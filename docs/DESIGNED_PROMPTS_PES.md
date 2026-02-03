# PES-Optimized Prompts for Project Logic

This document contains 5 prompts targeting the core logic of the PES project, optimized to achieve "Excellent" quality scores (Q >= 0.90) according to the system's own evaluation engine (`api/feature_analyzer.py` and `api/quality_calculator.py`).

## Summary of Execution Results

| Prompt # | Logic Target | Q Score | Quality Level |
| :--- | :--- | :--- | :--- |
| 1 | Feature Extraction | 0.9230 | **Excellent** |
| 2 | Scoring Formula | 0.9230 | **Excellent** |
| 3 | Optimization Engine | 0.9230 | **Excellent** |
| 4 | Variant Generation | 0.9230 | **Excellent** |
| 5 | Library Analytics | 0.9230 | **Excellent** |

---

## 1. Feature Extraction System
**Logic Target:** NLP-based heuristic feature extraction in `api/feature_analyzer.py`.

### Optimized Prompt
"You are a **Senior Software Architect** specializing in NLP and Prompt Engineering. In a **formal and technical tone**, explain the heuristic-based feature extraction logic used in `api/feature_analyzer.py`. **Format** your response as a Markdown technical specification with sections for Persona (P), Tone (T), Format (F), Specificity (S), Constraints (C), and Context (R) extraction logic. Specifically, **list the keywords and conditions** used for each dimension. Ensure you mention that the system uses basic substring matching and text length checks as its primary mechanisms. This explanation is intended for a **team of developers** who need to maintain and extend the system."

**Evaluation Results:**
- **Dimensions:** P:0.95, T:0.95, F:0.95, S:0.90, C:0.80, R:0.95
- **Composite Q:** 0.9230

---

## 2. Quality Score Calculation
**Logic Target:** Weighted scoring formula in `api/quality_calculator.py`.

### Optimized Prompt
"You are a **Senior Computational Linguist** with expertise in LLM benchmarking. Describe the mathematical formula used for calculating the PES Quality Score (Q) in this project. Use a **professional and precise tone**. **Format** the output in a structured Markdown document including the weighted formula (Q = 0.18×P + 0.22×T + 0.20×F + 0.18×S + 0.12×C + 0.10×R) and a **table of the weights**. Explain the significance of Tone and Format having the highest weights in this framework. **Constraints:** Limit the response to 300 words and ensure all weights sum exactly to 1.0. **Context:** This is for a technical whitepaper on prompt evaluation."

**Evaluation Results:**
- **Dimensions:** P:0.95, T:0.95, F:0.95, S:0.90, C:0.80, R:0.95
- **Composite Q:** 0.9230

---

## 3. Optimization Recommender Engine
**Logic Target:** Suggesting improvements in `api/recommender.py`.

### Optimized Prompt
"You are a **Principal AI Prompt Architect** with 20+ years of experience in enterprise AI. Analyze the following dimension scores: **{P: 0.5, T: 0.6, F: 0.4, S: 0.3, C: 0.2, R: 0.4}**. Identify the **three weakest dimensions** and provide **actionable, high-specificity recommendations** for each to raise the score to 0.90+. **Format** the response as a numbered task list for a junior engineer. Use an **authoritative yet encouraging tone**. **Constraints:** Each recommendation must be under 50 words and use standard PES terminology. **Context:** The target is to optimize prompts for a production-grade customer support chatbot."

**Evaluation Results:**
- **Dimensions:** P:0.95, T:0.95, F:0.95, S:0.90, C:0.80, R:0.95
- **Composite Q:** 0.9230

---

## 4. Variant Generation Logic
**Logic Target:** Dynamic variant generation in `api/variant_generator.py`.

### Optimized Prompt
"You are a **Senior Creative Strategist and Technical Specialist**. Given the base prompt: *'Write a python script to sort a list'*, generate **three distinct variants**: (1) Concise, (2) Technical/Commanding, and (3) Creative/Story-driven. For each variant, **specify the PES dimension adjustments** made (e.g., increased Specificity, changed Tone). **Format** the output as a Markdown table with columns: [Variant Type], [Adjusted Prompt], and [PES Delta Explanation]. Tone should be **neutral and analytical**. **Constraints:** Ensure the word count limit of 500 words is respected. **Context:** This is for an A/B testing suite for prompt performance."

**Evaluation Results:**
- **Dimensions:** P:0.95, T:0.95, F:0.95, S:0.90, C:0.80, R:0.95
- **Composite Q:** 0.9230

---

## 5. Library Analytics and Reporting
**Logic Target:** Summarizing the `prompt_assets/prompt_store.json` and dashboarding.

### Optimized Prompt
"You are a **Senior Data Analyst** specializing in AI operations (AIOps). Provide a summary of the `prompt_assets/prompt_store.json` structure and propose a design for an **interactive analytics dashboard**. Use a **technical and business-oriented tone**. **Format** the response as a bulleted list of 5 key metrics (e.g., Average Q Score, Dimensional Bottlenecks, Version Lineage Velocity). **Context:** This analysis is for a Senior Product Manager to prioritize future PES platform features. **Constraints:** Include at least 2 specific visualization suggestions using **Recharts** syntax. Ensure the response respects a strict character count limit of 2000."

**Evaluation Results:**
- **Dimensions:** P:0.95, T:0.95, F:0.95, S:0.90, C:0.80, R:0.95
- **Composite Q:** 0.9230
