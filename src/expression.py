from tokenizer import Token
from objects import Expression, Comprasion
from error import error

COMPARE = [
    ">", "<",
    ">=", "<=", "==", "!="
]

ARITH = [
    "+", "-", "*", "/",
    "%",
    "|", "&", "^", "~"
]

def parse_expressions(tokens: list[Token, ...], orig: list[Token, ...]) -> list[Token, ...]:
    tok = []

    idx = 0
    while idx < len(tokens):
        el = tokens[idx]

        if isinstance(el, Token) and el.token in ARITH:
            # if idx - 1 < len(tok):
            if idx != 0:
                del tok[-1]  # del tok[idx -1]

            expr = [tokens[idx-1], el]
            sign = False

            idx += 1
            while True:
                if not sign:
                    if tokens[idx].token in ARITH:
                        print("Double sign!")
                        error(orig, tokens[idx], "Arithmetic error: Double sign!",
                              tokens[idx].start, tokens[idx].end)
                        exit(1)
                    else:
                        expr.append(tokens[idx])
                        sign = True
                else:
                    if idx >= len(tokens):
                        break
                    
                    if tokens[idx].token in ARITH:
                        expr.append(tokens[idx])
                        sign = False
                    else:
                        break
                idx += 1
            tok.append(Expression(
                expr,
                expr[0].line
            ))
            tok.append(tokens[idx])
        else:
            tok.append(el)
        idx += 1
    return tok

def parse_comprasions(tokens: list[Token, ...], orig: list[Token, ...]) -> list[Token, ...]:
    tok = []

    idx = 0
    while idx < len(tokens):
        el = tokens[idx]

        if idx+1 < len(tokens) and (isinstance(tokens[idx+1], Token) and tokens[idx+1].token in COMPARE):
            what = el
            sign = tokens[idx+1].token
            with_ = tokens[idx+2]

            tok.append(Comprasion(
                what, sign, with_
            ))
            idx += 3
            continue
        else:
            tok.append(el)
        idx += 1

    return tok
