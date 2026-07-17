def roi(initial, final):

    return ((final - initial) / initial) * 100


def profit(initial, final):

    return final - initial


def win_rate(wins, total):

    if total == 0:

        return 0

    return (wins / total) * 100