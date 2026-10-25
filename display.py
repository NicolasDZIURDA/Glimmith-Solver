import string
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection

def display_solution(grid, solution, wall_list=None):
    """Affiche les régions dans le terminal et crée solution.png."""
    height = len(grid)
    width = len(grid[0])

    fig, ax = plt.subplots(figsize=(width, height))
    cmap = plt.colormaps["tab20"]
    
    valid_cells = {
    (r, c)
    for r in range(height)
    for c in range(width)
    if grid[r][c] == "."
    }

    contours = []

    for r, c in valid_cells:
        # Bord supérieur
        if (r - 1, c) not in valid_cells:
            contours.append([(c, height - r), (c + 1, height - r)])

        # Bord inférieur
        if (r + 1, c) not in valid_cells:
            contours.append([
                (c, height - 1 - r),
                (c + 1, height - 1 - r)
            ])

        # Bord gauche
        if (r, c - 1) not in valid_cells:
            contours.append([
                (c, height - 1 - r),
                (c, height - r)
            ])

        # Bord droit
        if (r, c + 1) not in valid_cells:
            contours.append([
                (c + 1, height - 1 - r),
                (c + 1, height - r)
            ])

    ax.add_collection(
        LineCollection(contours, colors="black", linewidths=4)
    )

    walls = {
        frozenset((tuple(a), tuple(b)))
        for a, b in (wall_list or [])
    }
    
    for index, region in enumerate(solution):

        for r, c in region:
            ax.add_patch(Rectangle(
                (c, height - 1 - r),
                1, 1,
                facecolor=cmap(index % 20),
                edgecolor="black",
                linewidth=1,
            ))

    for r in range(height):
        for c in range(width):
            if grid[r][c] == "#":
                ax.add_patch(Rectangle(
                    (c, height - 1 - r),
                    1, 1,
                    facecolor="lightgray",
                    edgecolor="black",
                ))
                
    for wall in walls:
        a, b = tuple(wall)
        r1, c1 = a
        r2, c2 = b

        if r1 == r2:
            # Séparation verticale entre deux colonnes.
            x = max(c1, c2)
            y = height - 1 - r1
            ax.plot(
                [x, x], [y, y + 1],
                color="black", linewidth=4,
                solid_capstyle="butt",
            )
        else:
            # Séparation horizontale entre deux lignes.
            x = c1
            y = height - max(r1, r2)
            ax.plot(
                [x, x + 1], [y, y],
                color="black", linewidth=4,
                solid_capstyle="butt",
            )

    print("\nSolution :")

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.savefig("solution.png", dpi=200, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    print("\nImage enregistrée dans solution.png")