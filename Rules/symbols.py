def has_too_many_symbols(region, symbol_positions):
    """Vérifie si une région contient plusieurs symboles du même type."""
    return any(
        sum(cell in positions for cell in region) > 1
        for positions in symbol_positions.values()
    )


def has_one_each_symbol(region, symbol_positions):
    """Vérifie qu'une région contient exactement un symbole de chaque type."""
    return all(
        sum(cell in positions for cell in region) == 1
        for positions in symbol_positions.values()
    )
    

def generate_symbol_regions(
    valid,
    height,
    width,
    walls,
    symbol_positions,
    neighbors,
    crosses_wall,
    region_size=None,
):
    """Génère les régions connexes contenant exactement
    un symbole de chaque type.
    """
    all_symbol_cells = set().union(*symbol_positions.values())
    all_regions = set()

    # Une région démarre sur chaque symbole du premier type.
    symbol_types = list(symbol_positions)
    
    if not symbol_types:
        return []

    first_type = symbol_types[0]
    first_symbols = symbol_positions[first_type]

    for start in first_symbols:
        regions = {frozenset({start})}
        seen = set(regions)
        print(len(regions))

        while regions:
            expanded = set()

            for region in regions:
                if (
                    has_one_each_symbol(region, symbol_positions)
                    and (
                        region_size is None
                        or len(region) == region_size
                    )
                ):
                    all_regions.add(region)

                if (
                    region_size is not None
                    and len(region) >= region_size
                ):
                    continue

                for cell in region:
                    for neighbor in neighbors(
                        cell, height, width, valid, walls
                    ):
                        if neighbor in region:
                            continue

                        if crosses_wall(region, neighbor, walls):
                            continue

                        new_region = region | {neighbor}

                        if has_too_many_symbols(
                            new_region, symbol_positions
                        ):
                            continue

                        if new_region not in seen:
                            seen.add(new_region)
                            expanded.add(new_region)

            regions = expanded

    return list(all_regions)
