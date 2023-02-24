# Handles font requests and returns appropriate directory path to parent file
# NOTE: Only returns directory path as STRING and does NOT return FONT data.

assets = 'assets/fonts/'


def load(bold=False, bar=False, three_d=False):
    path = assets
    if not bar:
        path += 'no_bar'
    if three_d:
        path += '3D'
    if bold:
        path += 'bold' if path == assets else '_bold'

    if path == assets:
        path += 'default'

    return path + '.ttf'
