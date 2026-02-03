
## 2026-02-01 - [Inefficient Analytics Aggregation]
**Learning:** The `/api/analytics` endpoint was fetching the entire `PromptModel` library into memory using `.query.all()` just to calculate averages and distributions. This is an O(N) operation in terms of memory and network traffic that degrades linearly with database size.
**Action:** Use database-level aggregation functions like `func.avg()` and `func.count()` to perform computations on the database server, returning only the results to the application.

## 2026-02-01 - [Single-Pass Aggregation]
**Learning:** Calculating distribution stats using multiple `.count()` queries is inefficient as it results in multiple database roundtrips.
**Action:** Use `func.sum(case(...))` to compute multiple metrics in a single SQL query.

## 2026-02-01 - [Scalable Listing with Pagination]
**Learning:** Returning all items in a list view (`.all()`) leads to performance degradation as the database grows.
**Action:** Always implement pagination on the backend (`.paginate()`) and "Load More" on the frontend to ensure O(1) memory and network usage per request regardless of total data size.

## 2026-02-01 - [Fast String Scanning with Regex]
**Learning:** Python's `any(c.isdigit() for c in s)` is much slower than `re.search(r'\d', s)` for large strings because the latter is implemented in C and stops at the first match more efficiently.
**Action:** Use Regex for simple character set checks on large text inputs.
