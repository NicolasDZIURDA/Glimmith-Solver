from regions import generate_regions

def solve(puzzle, max_solutions=2):
    """Recherche des partitions complètes, jusqu'à max_solutions."""
    region_size = next(
        (rule["value"] for rule in puzzle["rules"] if rule["type"] == "precision"),
        None
    )
    
    valid, regions = generate_regions(puzzle, region_size)

    if region_size is not None and len(valid) % region_size != 0:
        return []

    if max_solutions < 1:
        raise ValueError("max_solutions doit être supérieur à zéro.")

    by_cell = {cell: [] for cell in valid}

    for region in regions:
        for cell in region:
            by_cell[cell].append(region)

    solutions = []

    def search(remaining, chosen):
        if len(solutions) >= max_solutions:
            return

        if not remaining:
            solutions.append(list(chosen))
            return

        # Choisir la case restante qui a le moins de possibilités.
        cell = min(
            remaining,
            key=lambda c: sum(
                region <= remaining
                for region in by_cell[c]
            ),
        )

        for region in by_cell[cell]:
            if region <= remaining:
                search(remaining - region, chosen + [region])

                if len(solutions) >= max_solutions:
                    return

    search(frozenset(valid), [])
    return solutions
