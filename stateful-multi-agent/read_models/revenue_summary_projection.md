# RevenueSummaryProjection

**Purpose:**
Maintains real-time aggregate stats of all order payments and refunds—summarized by day, month, week, and in total.

## Consumed Events
- `OrderPaid`
- `OrderRefunded`

## Projection Structure
- `totals`: 'paid', 'refunded', 'net', 'orders', 'refunds'
- `by_day`, `by_month`, `by_week`: same fields, rolled up by each period

## Provided Queries
- `get_total()`
- `get_by_day(day)`
- `get_by_month(month)`
- `get_by_week(week)`

## Example Usage
```python
projection.handle(OrderPaid(...))
today_summary = projection.get_by_day(date.today())
net = projection.get_total()['net']
```

---
Essential for finance dashboards, management reporting, and forecast tools.
