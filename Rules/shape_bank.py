from Rules.symbols import *

def generate_shape_regions(puzzle, valid, walls):
    height = len(puzzle["grid"])
    width = len(puzzle["grid"][0])
    rules = {rule["type"] for rule in puzzle["rules"]}
    symbol_positions = {
        name: {tuple(pos) for pos in positions}
        for name, positions in (puzzle.get("symbols") or {}).items()
    }
     
    all_regions = set()
    
    transformations = [
        lambda r, c: (r, c),
        lambda r, c: (r, -c),
        lambda r, c: (-r, c),
        lambda r, c: (-r, -c),
        lambda r, c: (c, r),
        lambda r, c: (c, -r),
        lambda r, c: (-c, r),
        lambda r, c: (-c, -r),
    ]

    for shape in puzzle.get("shape_bank", []):
        variants = set()

        for transform in transformations:
            transformed = [
                transform(r, c) for r, c in shape
            ]
            min_r = min(r for r, c in transformed)
            min_c = min(c for r, c in transformed)

            variant = tuple(sorted(
                (r - min_r, c - min_c)
                for r, c in transformed
            ))
            variants.add(variant)

        for variant in variants:
            shape_height = max(r for r, c in variant) + 1
            shape_width = max(c for r, c in variant) + 1

            for start_r in range(height - shape_height + 1):
                for start_c in range(width - shape_width + 1):
                    region = frozenset(
                        (start_r + r, start_c + c)
                        for r, c in variant
                    )

                    if not region <= valid:
                        continue

                    if any(wall <= region for wall in walls):
                        continue

                    if (
                        "symbols" in rules
                        and not has_one_each_symbol(
                            region, symbol_positions
                        )
                    ):
                        continue

                    all_regions.add(region)

    print(f"Placements valides de la banque : {len(all_regions)}")
    return valid, list(all_regions)