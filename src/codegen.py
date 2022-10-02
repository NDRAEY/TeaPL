from tokenizer import Token
from objects import *
from random import randint
from action import Action, ActionType

def randstr() -> str:
    return ''.join([chr(randint(ord('a'), ord('z'))) for t in range(10)])

def to_ctype(typ: str) -> str:
    if typ=="ubyte": return "unsigned char"
    if typ=="byte": return "char"
    if typ=="ushort": return "unsigned short"
    if typ=="short": return "short"
    if typ=="uint": return "unsigned int"
    if typ=="int": return "int"
    if typ=="string": return "char*"
    if typ=="bool": return "char"

def build_args(variables: list[Variable], args: list[Token]) -> str:
    total = ""

    for n, i in enumerate(args):
        total += i.token
        if n!=len(args)-1:
            total += ", "
    
    return total
    ...

def codegen(actions: list[Action]) -> str:
    code = ""
    funccode = ""

    variables = []

    idx = 0
    while idx < len(actions):
        el = actions[idx]  # element

        need = el.args
        if el.type == ActionType.ASSIGNATION:
            vtype = to_ctype(need.type)
            vname = need.name
            vvalue = need.value.token

            code += f"{vtype} {vname} = {vvalue};\n"
            variables.append(need)

        elif el.type == ActionType.FUNC_CALL:
            fname = need.name
            fargs = need.args

            prepargs = build_args(variables, fargs)

            code += f"{fname}({prepargs});\n"

        elif el.type == ActionType.MATH:
            on = need.on.token
            op = need.operation
            val = need.value

            code += f"{on} {op}= {val};\n"
        idx += 1

    allcode = funccode + "\n\n"

    allcode += "int main(int argc, char** argv) {\n"+code+"\n}"

    return allcode
