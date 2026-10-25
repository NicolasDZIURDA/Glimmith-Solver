import json
from pathlib import Path
from solver import solve
from display import display_solution

path = Path(__file__).parent / "puzzle.json"

with path.open("r", encoding="utf-8") as file:
    data = json.load(file)

def choose_puzzle():
    puzzles = data["puzzles"]

    while True:
        try:
            choice = int(input(
                f"Choisis un puzzle entre 1 et {len(puzzles)} : "
            ))

            if not 1 <= choice <= len(puzzles):
                print(f"Erreur : choisis un nombre entre 1 et {len(puzzles)}.")
                continue

            return puzzles[choice - 1]

        except ValueError:
            print("Erreur : saisis un nombre entier.")

def validate_grid(grid):
    if not grid:
        raise ValueError("La grille est vide.")

    if not all(isinstance(row, str) for row in grid):
        raise ValueError("Chaque ligne doit être une chaîne de caractères.")

    if len(grid[0]) == 0:
        raise ValueError("Les lignes de la grille ne peuvent pas être vides.")

    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("Les lignes ont des longueurs différentes.")

    for row_index, row in enumerate(grid):
        for col_index, char in enumerate(row):
            if char not in {".", "#"}:
                raise ValueError(f"Caractère invalide '{char}' ")

    print("Grille valide.")

puzzle = choose_puzzle()

validate_grid(puzzle["grid"])

supported_rules = ["precision", "symbols"]

unsupported = [
    rule["type"]
    for rule in puzzle["rules"]
    if rule["type"] not in supported_rules
]

if unsupported:
    raise ValueError(f"Règles non encore implémentées : {unsupported}")

region_size = next(
    (rule["value"] for rule in puzzle["rules"] if rule["type"] == "precision"),
    None
)

solutions = solve(puzzle, max_solutions=2)

if len(solutions) == 0:
    print("Aucune solution.")
elif len(solutions) == 1:
    print("Une solution trouvée.")
    print("Attention : l'unicité n'est confirmée que si "
            "la recherche a été exhaustive.")
    display_solution(puzzle["grid"], solutions[0], wall_list=puzzle.get("walls", []))
else:
    print("Plusieurs solutions : au moins 2.")
    display_solution(puzzle["grid"], solutions[0], wall_list=puzzle.get("walls", []))