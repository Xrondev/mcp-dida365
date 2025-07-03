from datetime import datetime, timedelta, date
from typing import Any, Callable, Dict, List

# 1) Supported operators
_OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
}

# 2) Named priority levels → numeric
_PRIORITY_MAP = {"none": 0, "low": 1, "medium": 3, "high": 5}


def _parse_iso_date(s: str) -> date:
    # Example format: "2025-07-02T16:00:00.000+0000"
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z").date()


def _resolve_date_keyword(kw: str) -> date:
    today = datetime.now().date()
    if kw.lower() == "yesterday":
        return today - timedelta(days=1)
    if kw.lower() == "today":
        return today
    if kw.lower() == "tomorrow":
        return today + timedelta(days=1)
    return datetime.strptime(kw, "%Y-%m-%d").date()


def _build_predicate(expr: str) -> Callable[[Dict[Any, Any]], bool]:
    """
    Turn a string like "dueDate == tomorrow" into a
    function that returns True/False for each task.
    """
    parts = expr.split(maxsplit=2)
    if len(parts) != 3:
        raise ValueError(f"Invalid filter expression: {expr!r}")
    field, op, raw_val = parts

    if op not in _OPERATORS:
        raise ValueError(f"Unsupported operator {op!r} in {expr!r}")

    cmp_fn = _OPERATORS[op]

    def predicate(task: Dict[Any, Any]) -> bool:
        if field not in task:
            return False
        val = task[field]

        # ——— Date fields ———
        if "date" in field.lower():
            try:
                actual = _parse_iso_date(val)
            except Exception:
                return False
            expected = _resolve_date_keyword(raw_val)
            return cmp_fn(actual, expected)

        # ——— Priority keyword or numeric ———
        if field.lower() == "priority":
            actual = int(val)
            expected = _PRIORITY_MAP.get(raw_val.lower(), None)
            if expected is None:
                # maybe raw_val was a number
                expected = int(raw_val)
            return cmp_fn(actual, expected)

        # ——— Numeric fields ———
        if isinstance(val, (int, float)):
            return cmp_fn(val, type(val)(raw_val))

        # ——— Fallback to string comparison ———
        return cmp_fn(str(val), raw_val)

    return predicate


def filter_task(
    tasks: List[Dict[Any, Any]], filter_fields: List[str]
) -> List[Dict[Any, Any]]:
    """
    Return only those tasks for which **all** filter expressions match.
    """
    preds = [_build_predicate(expr) for expr in filter_fields]
    return [task for task in tasks if all(pred(task) for pred in preds)]
