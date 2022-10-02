"""
Charmeleon: Join tokenized strings into one string (internal)
"""

from tokenizer import Token
from error import error
from objects import FunctionCall, Block
from expression import parse_expressions as exprp

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

        if i.token == "\"":
            first = i

            idx += 1

            collect = []
            while True:
                if idx>=len(tokens):
                    error(tokens, first, "Unexcepted EOF", first.start, tokens[idx-1].end)

                if tokens[idx].token=="\"":
                    break

                collect.append(tokens[idx].token)
                idx += 1

            last = tokens[idx]
            tok.append(Token("\""+''.join(collect)+"\"", first.start, last.end, last.line))
        elif idx+1 < len(tokens) and tokens[idx+1].token == "(":  # Function call
            name = tokens[idx].token
            args = []

            tks = [tokens[idx], tokens[idx+1]]

            idx+=2
            level = 1
            while True:
                if tokens[idx].token == "(":
                    level += 1
                if tokens[idx].token == ")":
                    level -= 1
                if level == 0: break
                args.append(tokens[idx])
                tks.append(tokens[idx])
                idx += 1
            tks.append(tokens[idx])

            args = exprp(pretty(args, origtk), origtk)

            z = 0
            while z < len(args):
                if isinstance(args[z], Token) and args[z].token in (",", " "):
                    del args[z]
                    continue
                z += 1
            tok.append(FunctionCall(name, args, tks, tks[0].line))
            idx += 1
        elif tokens[idx].token == "{":
            block = []

            level = 1
            idx += 1
            while True:
                if tokens[idx].token == "{": level += 1
                if tokens[idx].token == "}": level -= 1
                if level==0: break

                block.append(tokens[idx])
                idx += 1
            tok.append(Block(block, block[0].line))
            # idx += 1
        else:
            tok.append(i)
        idx += 1
    return tok
