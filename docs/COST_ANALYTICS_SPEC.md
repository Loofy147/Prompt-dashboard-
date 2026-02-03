# Technical Specification: Cost Analytics Dashboard

**Target Audience**: Finance Managers, Prompt Architects
**Goal**: Visualize AI spend and ROI of prompt optimization.

## 1. Visual Requirements

### Spend Summary (StatCards)
- **Total Cost**: Sum of `total_cost_usd` across all optimization records.
- **Efficiency (ΔQ/$)**: Average quality improvement per dollar spent.
- **Token Velocity**: Total tokens processed per day.

### Recharts Visualizations
- **Line Chart**: "Daily Burn Rate" (X-axis: Date, Y-axis: USD).
- **Bar Chart**: "Provider Efficiency" (Comparison of cost per 0.1 Q gain between Claude and OpenAI).
- **Radar Chart**: "PES Improvement" (Before/After comparison of average dimension scores).

## 2. Technical Architecture

### Component Hierarchy (React)
```typescript
FinanceView
├── SpendHeader (Stats)
├── BurnRateChart (LineChart)
├── EfficiencyComparison (BarChart)
└── TopSpenderTable (DataTable)
```

### State Management
- **Key**: `['analytics', 'costs', dateRange]`
- **Source**: New `/api/analytics/costs` endpoint (to be implemented).

### Styling (Tailwind CSS)
- **Primary**: `bg-palette-primary` (Indigo 600)
- **Secondary**: `bg-palette-secondary` (Pink 500)
- **Success/Warning**: Emerald-500 for savings, Amber-500 for high spend alerts.

## 3. Integration Points
The dashboard will pull data from the `OptimizationIteration` table (via the `iterations_json` in the `PromptModel` or a new dedicated tracking table).

## 4. User Workflow
1. User clicks "Finance" tab.
2. Selects "Last 30 Days".
3. Dashboard identifies that OpenAI is 20% more expensive for a specific "Technical Spec" domain.
4. User updates project settings to prefer Anthropic for that domain.

---
*Design by Lead Product Designer Agent*
