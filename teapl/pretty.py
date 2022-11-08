"""
Charmeleon: Join tokenized strings into one string (internal)
"""

try:
    from teapl.tokenizer import Token, TOKENLIST
    from teapl.error import error
    from teapl.objects import *
    from teapl.expression import parse_expressions as exprp
    import teapl.utils as utils
except:
    from tokenizer import Token, TOKENLIST
    from error import error
    from objects import *
    from expression import parse_expressions as exprp
    import utils

def select_line(tokens: list[Token], line: int) -> list[Token, ...]:
    t = []
    for i in tokens:
        if i.line == line:
            t.append(i)
    return t

def remove_whitespaces(tokens: list[Token]) -> list[Token, ...]:
    t = []
    for i in tokens:
        if not isinstance(i, Token):
            t.append(i)
            continue
            
        if i.token != " ":
            t.append(i)
    return t

def pretty(tokens: list[Token, ...], origtk: list[Token]) -> list[Token, ...]:
    tok = []
    idx = 0

    while idx < len(tokens):
        i = tokens[idx]

        if not isinstance(i, Token):
            tok.append(i)
            idx += 1
            continue

        if i.token == "\"":  # Strings
            first = i

            idx += 1

            collect = []
            while True:
                if idx>=len(tokens):
                    error(tokens, first, "Unexcepted end", first.start, tokens[idx-1].end)

                if tokens[idx].token=="\"":
                    break

                collect.append(tokens[idx].token)
                idx += 1

            last = tokens[idx]
            tok.append(Token("\""+''.join(collect)+"\"", first.start, last.end, last.line))
            
        elif i.token=="\'":
            first = i
            idx += 1
            collect = []

            while True:
                if idx >= len(tokens):
                    error(tokens, first, "Unexcepted end", first.start, tokens[idx-1].end)
                if tokens[idx].token=="\'":
                    break
                collect.append(tokens[idx].token)
                idx += 1
            
            last = tokens[idx]
            tok.append(Token("\'"+''.join(collect)+"\'", first.start, last.end, last.line))
            
        elif tokens[idx].token == "(":
            collected = []

            idx+=1
            level = 1
            while True:
                if tokens[idx].token == "(":
                    level += 1
                if tokens[idx].token == ")":
                    level -= 1
                if level == 0: break
                collected.append(tokens[idx])
                idx += 1
            
            tok.append(Group(collected))
            # idx += 1
        elif tokens[idx].token == "{":  # Blocks
            block = []

            level = 1
            idx += 1
            while True:
                if tokens[idx].token == "{": level += 1
                if tokens[idx].token == "}": level -= 1
                if level==0: break

                block.append(tokens[idx])
                idx += 1
            tok.append(Block(block, block[0].start, block[-1].end, block[0].line))
            # idx += 1
        elif tokens[idx].token == "//":
            idx += 1
            while True:
                if tokens[idx].token == "\n": break
                idx += 1
        else:
            tok.append(i)
        idx += 1
    return tok

def build_funccalls(tokens, orig: list[Token]) -> list[Token, ...]:
    tok = []
    idx = 0

    while idx < len(tokens):
        el = tokens[idx]

        if isinstance(el, Token) and idx + 1 < len(tokens) and isinstance(tokens[idx+1], Group):
            args_raw = pretty(tokens[idx+1].tokens, orig)
            args = []

            for i in args_raw:
                # if isinstance(i, Token) and i.token in (" ", ","): continue
                args.append(i)
            
            tok.append(FunctionCall(el.token, args, args_raw, el.line))
            idx += 1
        else:
            tok.append(el)
        
        idx += 1
    return tok

def build_arrays(tokens, orig: list[Token]) -> list[Token, ...]:
    tok = []
    idx = 0

    while idx < len(tokens):
        el = tokens[idx]

        if isinstance(el, Token) and el.token == "[":
            collected = []

            idx += 1
            level = 1
            while True:
                if tokens[idx].token == "[":
                    level += 1
                if tokens[idx].token == "]":
                    level -= 1
                if level == 0: break
                collected.append(tokens[idx])
                idx += 1
            tok.append(Array(utils.parse_code_tokenized_lite(collected, orig)))
        else:
            tok.append(el)
        
        idx += 1
    return tok

def build_indexes(tokens, orig: list[Token]) -> list[Token, ...]:
    tok = []
    idx = 0

    while idx < len(tokens):
        el = tokens[idx]

        if idx+1 < len(tokens):
            if isinstance(el, Token) and (el.token not in TOKENLIST):
                '''
                idx += 1
                nx = tokens[idx]
                if isinstance(nx, Array):
                    tok.append(IndexedValue(el, nx))
                else:
                    tok.extend([el, nx])
                '''
                idx += 1
                nx = []
                while idx < len(tokens) and isinstance(tokens[idx], Array):
                    nx.append(tokens[idx])
                    idx += 1
                if len(nx) != 0:
                    tok.append(IndexedValue(el, nx))
                else:
                    tok.append(el)
                
                continue
            else:
                tok.append(el)
        else:
            tok.append(el)
        
        idx += 1

    return tok
