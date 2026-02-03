
## 2026-02-01 - [Inefficient Analytics Aggregation]
**Learning:** The `/api/analytics` endpoint was fetching the entire `PromptModel` library into memory using `.query.all()` just to calculate averages and distributions. This is an O(N) operation in terms of memory and network traffic that degrades linearly with database size.
**Action:** Use database-level aggregation functions like `func.avg()` and `func.count()` to perform computations on the database server, returning only the results to the application.
