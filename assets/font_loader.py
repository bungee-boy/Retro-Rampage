# Handles font requests and returns appropriate directory path to parent file
# NOTE: Only returns directory path as STRING and does NOT return FONT data.

assets = 'assets\\fonts\\'


def load(bold=False, italic=False, bar=False, outline=False, three_d=False):
    path = assets
    if not bar:
        path += 'no_bar'
    elif outline:
        path += 'outline'
    elif three_d:
        path += '3D'
    else:
        path += ''

    if bold:
        if path == assets:
            path += 'bold'
        else:
            path += '_bold'
    if italic:
        if path == assets:
            path += italic
        else:
            path += '_italic'

    if path == assets:
        path += 'default'

    return path + '.ttf'
