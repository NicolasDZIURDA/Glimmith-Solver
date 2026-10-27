from Rules.symbols import *
from Rules.shape_bank import *

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
    
    symbols = puzzle.get("symbols") or {}
    symbol_positions = {
        symbol_type: {tuple(pos) for pos in positions}
        for symbol_type, positions in symbols.items()
    }
    
    if "symbols" in rules and "shape_bank" not in rules:
        print("Test passé")
        return valid, generate_symbol_regions(
            valid,
            height,
            width,
            walls,
            symbol_positions,
            neighbors,
            crosses_wall,
            region_size,
        )
    
    # Génération directe pour la banque de formes
    if "shape_bank" in rules:
        return generate_shape_regions(puzzle, valid, walls)

    # Chaque case valide constitue une région
    regions = {frozenset({cell}) for cell in valid}
    all_regions = set(regions)

    while regions:
        expanded = set()
        print("ici")

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