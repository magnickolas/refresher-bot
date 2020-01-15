from editdistance import eval

from sync_to_async import make_async


@make_async
def calculate(s: str, t: str):
    return eval(s, t)
