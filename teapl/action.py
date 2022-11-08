# How you call this? AST?

from enum import Enum
from pprint import pprint

try:
    from teapl.error import error
    from teapl.tokenizer import Token
    from teapl.objects import *
    from teapl.utils import *
except:
    from error import error
    from tokenizer import Token
    from objects import *
    from utils import *

class ActionType(Enum):
    ASSIGNATION = 0
    FUNC_CALL = 1
    CONDITION = 2
    MATH = 3
    WHILE_LOOP = 4
    FUNCTION = 5
    RETURN = 6
    C_EXTERN = 7

@dataclass
class Action:
    type: ActionType
    metadata: dict
    args: Any

TYPES = [
    "bool",
    "byte",
    "ubyte",
    "short",
    "ushort",
    "int",
    "uint",
    "string"
]

COMPILE_TIME_VARS = []

def make_actions(tokens: list[Token, ...], orig: list[Token]) -> list[Action]:
    actions = []
    idx = 0

    # Remove whitespaces
    while idx < len(tokens):
        if isinstance(tokens[idx], Token) and tokens[idx].token in (" ", "\t"):
            del tokens[idx]
            continue
        idx += 1

    idx = 0

    while idx < len(tokens):
        i = tokens[idx]

        if isinstance(tokens[idx], Token) and i.token == "\n":
            idx += 1
            continue # I know

        if isinstance(i, Token) and (i.token in TYPES):            
            otype = i.token
            idx += 1

            i = tokens[idx]
            while i.token == "\n":
                idx += 1
                if idx >= len(tokens):
                    error(tokens, tokens[idx-1], "Unexcepted EOF",
                      tokens[idx-1].start, tokens[idx-1].start+1)

                i = tokens[idx]
            
            names = []
            while True:
                name = tokens[idx].token
                names.append(name)
                if tokens[idx+1].token != ",":
                    break
                if tokens[idx+2].token == "=":
                    idx += 1
                    break
                idx += 2  # If bug appears change this to 1.

            idx += 1
            if tokens[idx].token == "\n":  # If value was not specified
                for m in names:
                    actions.append(Action(
                        ActionType.ASSIGNATION,
                        {},
                        Variable(otype, m, DefaultVariable)
                    ))
                    COMPILE_TIME_VARS.append(Variable(otype, m, value))

            if tokens[idx].token == "=":
                idx += 1
                value = tokens[idx]

                if isinstance(value, FunctionCall):
                    tname = value.name
                    eline = value.line
                    targs = argsorig = value.args

                    print("N/A", tname, targs)
                    value = parse_code_tokenized_lite(targs, argsorig)
                    # value = build_args(value)

                    value = FunctionCall(tname, value, argsorig, eline)
                    print("Needs:", value)

                for m in names:
                    actions.append(Action(
                        ActionType.ASSIGNATION,
                        {},
                        Variable(otype, m, value)
                    ))
                    COMPILE_TIME_VARS.append(Variable(otype, m, value))
        elif isinstance(i, Token) and i.token == "if":
            conds = []
            idx += 1
            cond = tokens[idx]
            print("Condition: ", cond)
            idx += 1

            if idx >= len(tokens):
                error(tokens, tokens[idx-1], "Unexcepted EOF",
                      tokens[idx-1].start, tokens[idx-1].start+1)
            body = tokens[idx]

            conds.append(["if", cond, body])

            idx += 1
            while True:  # Check [elif]/else
                if idx >= len(tokens): break
                if tokens[idx].token != "\n": break
                idx += 1

            ...  # Check for elif(s) with loop here.
                
            while idx < len(tokens): # Check [elif]/else
                print(f"{idx}/{len(tokens)}")
                if tokens[idx].token == "else":
                    idx += 1
                    if idx >= len(tokens):
                        error(orig, tokens[idx - 1],
                              "Excepted Block, but EOF found!",
                              tokens[idx - 1].start, tokens[idx - 1].end)
                    if not isinstance(tokens[idx], Block):
                        if tokens[idx].token == "\n":
                            error(orig, tokens[idx],
                                  f"Excepted Block, but nothing found!",
                                  tokens[idx].start, tokens[idx].end)
                        else:        
                            error(orig, tokens[idx],
                                  f"Excepted Block, but other object found!",
                                  tokens[idx].start, tokens[idx].end)
                    elseblock = tokens[idx]
                    conds.append(["else", elseblock])
                    print("Added else")
                elif tokens[idx].token == "elif":
                    idx += 1
                    if idx >= len(tokens):
                        error(orig, tokens[idx - 1],
                              "Excepted Condition, but EOF found!",
                              tokens[idx - 1].start, tokens[idx - 1].end)
                    cond = tokens[idx]
                    idx += 1
                    elifblock = tokens[idx]
                    conds.append(["elif", cond, elifblock])
                else:
                    print("Stopping here... ", tokens[idx])
                    break
                idx += 1
                
            actions.append(Action(
                ActionType.CONDITION,
                {},
                conds
            ))
        elif isinstance(i, Token) and i.token == "while":
            idx += 1
            cond = tokens[idx]

            print("Condition: ", cond)

            idx += 1
            body = tokens[idx]

            actions.append(Action(
                ActionType.WHILE_LOOP,
                {},
                Loop(cond, body)
            ))
        elif isinstance(i, Token) and i.token == "func":
            idx += 1
            fcall = tokens[idx]

            fname, fargs = fcall.name, fcall.args
            
            # print("Name:", fname)
            # print("Args:", fargs)

            idx += 1
            fbody = tokens[idx]
            ret = None

            if (not isinstance(fbody, Block)) and isinstance(fbody, Token):
                ret = fbody.token
                idx += 1
                fbody = tokens[idx]

            # print("Return:", ret)
            # pprint(fbody)

            actions.append(Action(
                ActionType.FUNCTION,
                {},
                Function(fname, ret, fargs, fbody, i.line)
            ))
            idx += 1
        elif isinstance(i, Token) and i.token == "return":
            idx += 1
            ret = tokens[idx]

            actions.append(Action(
                ActionType.RETURN,
                {},
                Return(ret)
            ))
            idx += 1
        elif isinstance(i, Token) and i.token == "extern":
            idx += 1
            ret = tokens[idx]

            if not isinstance(ret, Block):
                error(orig, ret,
                      "Excepted Block!",
                      ret.start-1, ret.end-1)

            actions.append(Action(
                ActionType.C_EXTERN,
                {},
                ret
            ))
            idx += 1
        elif isinstance(i, FunctionCall):
            actions.append(Action(
                ActionType.FUNC_CALL,
                {},
                i
            ))
        elif isinstance(i, Token):
            print("First token:", i)

            idx += 1
            nxtoken = tokens[idx]

            print("Next token:", nxtoken)

            if isinstance(nxtoken, Block):
                error(orig, tokens[idx],
                      "Unexcepted Block!",
                      tokens[idx - 1].start, tokens[idx].end)

            if nxtoken.token == "--":
                actions.append(Action(
                    ActionType.MATH,
                    {},
                    MathOperationVariable(i, "-", 1)
                ))
            elif nxtoken.token == "++":
                actions.append(Action(
                    ActionType.MATH,
                    {},
                    MathOperationVariable(i, "+", 1)
                ))
            elif nxtoken.token == "+=":
                idx += 1
                actions.append(Action(
                    ActionType.MATH,
                    {},
                    MathOperationVariable(i, "+", tokens[idx].token)
                ))
            elif nxtoken.token == "-=":
                idx += 1
                actions.append(Action(
                    ActionType.MATH,
                    {},
                    MathOperationVariable(i, "-", tokens[idx].token)
                ))
            elif nxtoken.token == "/=":
                idx += 1
                actions.append(Action(
                    ActionType.MATH,
                    {},
                    MathOperationVariable(i, "/", tokens[idx].token)
                ))
            elif nxtoken.token == "*=":
                idx += 1
                actions.append(Action(
                    ActionType.MATH,
                    {},
                    MathOperationVariable(i, "*", tokens[idx].token)
                ))
            elif nxtoken.token == "=":
                idx += 1
                actions.append(Action(
                    ActionType.ASSIGNATION,
                    {"reassignation": True},
                    Variable(None, i.token, tokens[idx])
                ))
            elif nxtoken.token == "\n":
                error(tokens, tokens[idx-1], "(Maybe no operation) Newline is not supported!!!",
                      tokens[idx-1].start, nxtoken.end)
        elif isinstance(i, IndexedValue):
            typ = i.value.token
            arr = i.index

            if typ not in TYPES:
                error(orig, tokens[idx], f"Unknown type: {typ}",
                      tokens[idx].start, tokens[idx].end)

            addtyp = [typ, arr]
            
            idx += 1
            names = []
            while True:
                name = tokens[idx].token
                names.append(name)
                if tokens[idx+1].token != ",":
                    break
                if tokens[idx+2].token == "=":
                    idx += 1
                    break
                idx += 2

            idx += 1
            if tokens[idx].token == "=":
                idx += 1
                value = tokens[idx]

                for m in names:
                    actions.append(Action(
                        ActionType.ASSIGNATION,
                        {},
                        Variable(addtyp, m, value)
                    ))
                    COMPILE_TIME_VARS.append(Variable(addtyp, m, value))
        else:
            if isinstance(tokens[idx], Token):
                error(orig, tokens[idx], "Syntax Error or Unimplemented Action!",
                      tokens[idx].start, tokens[idx].end)
            elif isinstance(tokens[idx], Expression):
                error(orig, tokens[idx], "Syntax Error or Unimplemented Action!",
                      tokens[idx].tokens[0].start, tokens[idx].tokens[-1].end)
        idx += 1

    return actions
