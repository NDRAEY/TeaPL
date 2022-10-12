try:
    from teapl.tokenizer import Token
    from teapl.objects import Expression, Comprasion, Group
    from teapl.error import error
except:
    from tokenizer import Token
    from objects import Expression, Comprasion, Group
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

def expr2str(expr: Expression) -> str:
    s = ""

    print("=",expr)
    for i in expr.tokens:
        if isinstance(i, Expression):
            s += "("+expr2str(i)+")"
            continue
        s += i.token
        
    return s

def parse_expressions(tokens, orig: list[Token, ...]) -> list[Token, ...]:
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
                if idx >= len(tokens):
                    break
                if isinstance(tokens[idx], Token) and tokens[idx].token == "\n": break
                if not sign:
                    if isinstance(tokens[idx], Token) and tokens[idx].token in ARITH:
                        error(orig, tokens[idx], "Arithmetic error: Double sign!",
                              tokens[idx].start, tokens[idx].end)
                    else:
                        if isinstance(tokens[idx], Group):
                            prs = parse_expressions(tokens[idx].tokens, orig)[0]
                            expr.append(prs)
                        else:
                            expr.append(tokens[idx])
                        sign = True
                else:
                    if idx >= len(tokens): break
                    
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
            if idx < len(tokens):
                tok.append(tokens[idx])
            elif idx - 1 < len(tokens):
                if tokens[idx-1].token in ARITH:
                    error(orig, tokens[idx-1], "Unexpected arithmetic sign at end!",
                          tokens[idx-1].start, tokens[idx-1].end)
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

def check_expr(tokens, orig: list[Token, ...], expression: Expression):
    ...
