from symbols import *

def neighbors(cell, height, width, valid_cells, walls):
    """Retourne les voisins accessibles sans franchir de séparation."""
    r, c = cell

    for nr, nc in (
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
    ):
        if not (0 <= nr < height and 0 <= nc < width):
            continue

        neighbor = (nr, nc)

        if neighbor not in valid_cells:
            continue

        # Une séparation est indépendante du sens de parcours.
        edge = frozenset((cell, neighbor))

        if edge not in walls:
            yield neighbor

def crosses_wall(region, neighbor, walls):
    """Vérifie si l'ajout d'une case viole une séparation."""
    for wall in walls:
        a, b = tuple(wall)

        if (neighbor == a and b in region) or (
            neighbor == b and a in region
        ):
            return True

    return False

def validate_walls(wall_list, valid_cells):
    """Vérifie que les murs séparent bien deux cases adjacentes"""
    walls = set()
    
    for wall in wall_list or []:
        a, b = map(tuple, wall)

        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            raise ValueError(f"Séparation invalide : {wall}")

        if a not in valid_cells or b not in valid_cells:
            raise ValueError(f"Séparation hors grille ou sur une case absente : {wall}")

        walls.add(frozenset((a, b)))
        
    return walls

def normalize_shape(cells):
    """Retourne une signature indépendante de la position,
    de la rotation et de la symétrie de la forme.
    """
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

    variants = []

    for transform in transformations:
        transformed = [transform(r, c) for r, c in cells]

        min_r = min(r for r, c in transformed)
        min_c = min(c for r, c in transformed)

        normalized = tuple(sorted(
            (r - min_r, c - min_c)
            for r, c in transformed
        ))

        variants.append(normalized)
        
    return min(variants)
    

def generate_regions(puzzle, region_size):
    """Génère les régions connexes sans franchir les séparations."""
    height = len(puzzle["grid"])
    width = len(puzzle["grid"][0])

    valid = {
        (r, c)
        for r in range(height)
        for c in range(width)
        if puzzle["grid"][r][c] == "."
    }
    
    walls = validate_walls(puzzle.get("walls", []), valid)
    rules = {rule["type"] for rule in puzzle["rules"]}
    
    symbols = puzzle.get("symbols") or {}
    symbol_positions = {
        symbol_type: {tuple(pos) for pos in positions}
        for symbol_type, positions in symbols.items()
    }
    
    # Génération directe pour la banque de formes
    if "shape_bank" in rules:
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
                            "symbols_one_each" in rules
                            and not has_one_each_symbol(
                                region, symbol_positions
                            )
                        ):
                            continue

                        if (
                            "symbols" in rules
                            and has_too_many_symbols(
                                region, symbol_positions
                            )
                        ):
                            continue

                        all_regions.add(region)

        print(f"Placements valides de la banque : {len(all_regions)}")
        return valid, list(all_regions)

    # Chaque case valide constitue une région
    regions = {frozenset({cell}) for cell in valid}
    all_regions = set(regions)

    while regions:
        expanded = set()
        print(len(regions))

        for region in regions:
            if region_size is not None and len(region) >= region_size:
                continue
            
            for cell in region:
                for neighbor in neighbors(
                    cell, height, width, valid, walls
                ):
                    if neighbor in region:
                        continue

                    if crosses_wall(region, neighbor, walls):
                        continue
                    
                    if "symbols" in rules and has_too_many_symbols(
                        region | {neighbor}, symbol_positions
                    ):
                        continue
                    
                    expanded.add(region | {neighbor})
            
        all_regions.update(expanded)
        regions = expanded
        
    # Filtre sur la taille
    if "precision" in rules:
        all_regions = {
            region for region in all_regions
            if len(region) == region_size
        }
        
    # Filtre sur les symboles
    if "symbols" in rules:
        all_regions = {
            region for region in all_regions
            if has_one_each_symbol(region, symbol_positions)
        }
    
    return valid, list(all_regions)