
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

def generate_regions(grid, region_size, wall_list=None):
    """Génère les régions connexes sans franchir les séparations."""
    height = len(grid)
    width = len(grid[0])

    valid = {
        (r, c)
        for r in range(height)
        for c in range(width)
        if grid[r][c] == "."
    }
    
    walls = validate_walls(wall_list, valid)

    if region_size <= 0:
        raise ValueError("La taille des régions doit être positive.")

    if region_size > len(valid):
        return valid, []

    # Chaque case valide constitue une région
    regions = {frozenset({cell}) for cell in valid}

    for _ in range(1, region_size):
        expanded = set()

        for region in regions:
            for cell in region:
                for neighbor in neighbors(
                    cell, height, width, valid, walls
                ):
                    edge = frozenset((cell, neighbor))

                    if edge in walls:
                        continue

                    if neighbor not in region and not crosses_wall(region, neighbor, walls):
                        expanded.add(region | {neighbor})

        regions = expanded

    return valid, list(regions)


def solve(grid, region_size, wall_list=None, max_solutions=2):
    """Recherche des partitions complètes, jusqu'à max_solutions."""
    valid, regions = generate_regions(grid, region_size, wall_list)

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
