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