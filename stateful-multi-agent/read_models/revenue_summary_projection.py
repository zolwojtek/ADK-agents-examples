from typing import Dict, Any
from datetime import datetime, date

class RevenueSummaryProjection:
    """
    Projection that aggregates paid/refunded revenue by day/month/week and globally.
    Consumes OrderPaid and OrderRefunded events for up-to-date rollup statistics.
    """
    def __init__(self):
        self.totals = {
            'paid': 0.0,
            'refunded': 0.0,
            'net': 0.0,
            'orders': 0,
            'refunds': 0
        }
        self.by_day: Dict[date, Dict[str, Any]] = {}
        self.by_month: Dict[str, Dict[str, Any]] = {}  # YYYY-MM
        self.by_week: Dict[str, Dict[str, Any]] = {}   # YYYY-WW

    def handle(self, event: Any) -> None:
        event_type = getattr(event, "__event_type__", event.__class__.__name__)
        if event_type == "OrderPaid":
            self._on_paid(event)
        elif event_type == "OrderRefunded":
            self._on_refunded(event)
    
    def _on_paid(self, event):
        amount = getattr(event, "amount", None)
        if amount is None:
            amount = getattr(event, "total_amount", 0.0)
        else:
            amount = float(amount) if isinstance(amount, (float, int, str)) else 0.0
        occurred = getattr(event, "occurred_on", datetime.now())
        day = occurred.date()
        month = occurred.strftime("%Y-%m")
        week = f"{occurred.strftime('%Y')}-W{occurred.strftime('%V')}"

        self.totals['paid'] += amount
        self.totals['net'] += amount
        self.totals['orders'] += 1

        for period, d in [(day, self.by_day), (month, self.by_month), (week, self.by_week)]:
            if period not in d:
                d[period] = {'paid': 0.0, 'refunded': 0.0, 'net': 0.0, 'orders': 0, 'refunds': 0}
            d[period]['paid'] += amount
            d[period]['net'] += amount
            d[period]['orders'] += 1

    def _on_refunded(self, event):
        amount = getattr(event, "refund_amount", None)
        if amount is None:
            amount = getattr(event, "amount", 0.0)
        else:
            amount = float(amount) if isinstance(amount, (float, int, str)) else 0.0
        occurred = getattr(event, "occurred_on", datetime.now())
        day = occurred.date()
        month = occurred.strftime("%Y-%m")
        week = f"{occurred.strftime('%Y')}-W{occurred.strftime('%V')}"

        self.totals['refunded'] += amount
        self.totals['net'] -= amount
        self.totals['refunds'] += 1

        for period, d in [(day, self.by_day), (month, self.by_month), (week, self.by_week)]:
            if period not in d:
                d[period] = {'paid': 0.0, 'refunded': 0.0, 'net': 0.0, 'orders': 0, 'refunds': 0}
            d[period]['refunded'] += amount
            d[period]['net'] -= amount
            d[period]['refunds'] += 1

    def get_total(self) -> Dict[str, Any]:
        return self.totals.copy()

    def get_by_day(self, day: date) -> Dict[str, Any]:
        return self.by_day.get(day, {'paid': 0.0, 'refunded': 0.0, 'net': 0.0, 'orders': 0, 'refunds': 0}).copy()

    def get_by_month(self, month: str) -> Dict[str, Any]:
        return self.by_month.get(month, {'paid': 0.0, 'refunded': 0.0, 'net': 0.0, 'orders': 0, 'refunds': 0}).copy()

    def get_by_week(self, week: str) -> Dict[str, Any]:
        return self.by_week.get(week, {'paid': 0.0, 'refunded': 0.0, 'net': 0.0, 'orders': 0, 'refunds': 0}).copy()
