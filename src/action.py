from enum import Enum
from error import error
from tokenizer import Token

from objects import *

class ActionType(Enum):
    ASSIGNATION = 0
    FUNC_CALL = 1
    CONDITION = 2
    MATH = 3

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

        if isinstance(tokens[idx], Token) and (i.token in TYPES):
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
                idx += 2

            idx += 1
            if tokens[idx].token == "\n":
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
            what = tokens[idx]
            idx += 1
            sign = tokens[idx]
            idx += 1
            with_ = tokens[idx]

            cond = Condition(what, sign, with_)
            conds.append(["if", cond])

            idx += 1

            body = tokens[idx]
            print(body)

            idx += 1
            while True:  # Check [elif]/else
                if idx >= len(tokens): break
                if tokens[idx].token != "\n": break
                idx += 1

            ...  # Check for elif(s) with loop here.
                
            if idx < len(tokens): # Check [elif]/else
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
            actions.append(Action(
                ActionType.CONDITION,
                {},
                conds
            ))
        elif isinstance(i, Token) and i.token == "while":
            idx += 1
            cond = tokens[idx]

            print(cond)

            print("Loops unimplemented!")
            exit(1)
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
                    Variable(None, i.token, tokens[idx].token)
                ))
            # exit(1)
        else:
            error(orig, tokens[idx], "Syntax Error or Unimplemented Action!",
                  tokens[idx].start, tokens[idx].end);
        idx += 1

    return actions
