try:
    from tokenizer import Token
    from pretty import (pretty, remove_whitespaces,
                        build_arrays, build_indexes, build_funccalls)
    from expression import parse_comprasions, parse_expressions
    from objects import IndexedValue, FunctionCall
except:
    from teapl.tokenizer import Token
    from teapl.pretty import (pretty, remove_whitespaces,
                        build_arrays, build_indexes, build_funccalls)
    from teapl.expression import parse_comprasions, parse_expressions    
    from teapl.objects import IndexedValue, FunctionCall

def randstr() -> str:
    return ''.join([chr(randint(ord('a'), ord('z'))) for t in range(10)])

def parse_code_tokenized(tokens, orig: list[Token]) -> tuple[list[Token]]:
    tokenized = pretty(tokens, orig)
    tokenized = remove_whitespaces(tokenized)
    tokenized = parse_expressions(tokenized, orig)
    tokenized = parse_comprasions(tokenized, orig)
    tokenized = build_arrays(tokenized, orig)
    tokenized = build_indexes(tokenized, orig)
    tokenized = build_funccalls(tokenized, orig)
    return tokenized

def parse_code_tokenized_lite(tokens, orig: list[Token]) -> tuple[list[Token]]:
    tokenized = pretty(tokens, orig)
    tokenized = remove_whitespaces(tokenized)
    tokenized = parse_expressions(tokenized, orig)
    tokenized = build_arrays(tokenized, orig)
    tokenized = build_indexes(tokenized, orig)
    tokenized = build_funccalls(tokenized, orig)
    return tokenized

def indexed2c(val: IndexedValue) -> str:
    # TODO: Slices
    ids = ""
    for i in val.index:
        ids += "["+i.tokens[0].token+"]"
    return val.value.token + ids

def build_args(args: list[Token]) -> str:
    prep = []

    idx = 0
    while idx < len(args):
        el = args[idx]

        if isinstance(el, Token) and el.token == ",":
            idx += 1
            continue

        prep.append(el)
        idx += 1

    total = ""

    for n, i in enumerate(prep):
        if isinstance(i, Token):
            total += i.token
        elif isinstance(i, IndexedValue):
            total += indexed2c(i)
        elif isinstance(i, FunctionCall):
            total += f"{i.name}({build_args(i.args)})"
        
        if n+1 < len(prep):
            total += ", "

    return total
