def calculate_gross(components: list[dict]) -> float:
    return float(sum(c["amount"] for c in components))
