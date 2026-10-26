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

    # Chaque case valide constitue une région
    regions = {frozenset({cell}) for cell in valid}
    all_regions = set(regions)

    while regions:
        expanded = set()

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
    symbols = puzzle.get("symbols") or {}
    symbol_positions = {
        symbol_type: {tuple(pos) for pos in positions}
        for symbol_type, positions in symbols.items()
    }
    
    if "symbols" in rules:
        all_regions = {
            region for region in all_regions
            if has_one_each_symbol(region, symbol_positions)
        }
        
    region1 = frozenset({(0, 0), (0, 1), (0, 2), (0, 3)})
    region2 = frozenset({(0, 2), (1, 2), (2, 2), (3, 2)})
    print(f"Région 1 : {has_one_each_symbol(region1, symbol_positions)}")
    print(f"Région 2 : {has_one_each_symbol(region2, symbol_positions)}")

    return valid, list(all_regions)


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
