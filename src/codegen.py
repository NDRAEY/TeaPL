from tokenizer import Token
from objects import *
from random import randint
from action import Action, ActionType, make_actions
import pretty
import expression as expr

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

def find_var(variables: list, name: str):
    for i in variables:
        if i.name == name:
            return i

def codegen(actions: list[Action], wrap = True) -> str:
    code = ""
    funccode = ""

    variables = []

    idx = 0
    while idx < len(actions):
        el = actions[idx]  # element

        need = el.args
        if el.type == ActionType.ASSIGNATION:
            if "reassignation" not in el.metadata:
                vtype = to_ctype(need.type)
                vname = need.name
                vvalue = need.value.token
                code += f"{vtype} {vname} = {vvalue};\n"
                variables.append(need)
            else:
                vname = need.name
                vvalue = need.value.token
                code += f"{vname} = {vvalue};\n"
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

        elif el.type == ActionType.CONDITION:
            maincond = need[0][1]
            mainbody = mborig = need[0][2].tokens
            otherbodies = need[1:]

            maincond = [maincond.what.token, maincond.sign.token, maincond.with_.token]
            code += "if ("+' '.join(maincond)+") {\n"

            funcbody = pretty.pretty(mainbody, mborig)
            funcbody = pretty.remove_whitespaces(funcbody)
            funcbody = expr.parse_expressions(funcbody, mborig)
            funcbody = make_actions(funcbody, mborig)

            functot = codegen(funcbody, wrap=False)

            code += functot+"}"

            for mk in otherbodies:
                if mk[0]=="else":
                    body = borig = mk[1].tokens
                    code += "else{\n"

                    funcbody = pretty.pretty(body, borig)
                    funcbody = pretty.remove_whitespaces(funcbody)
                    funcbody = expr.parse_expressions(funcbody, borig)
                    funcbody = make_actions(funcbody, borig)
                    functot = codegen(funcbody, wrap=False)

                    code += functot+"}"
                    break
            ...  # For elif and else

            code += "\n"
        idx += 1

    if wrap:
        allcode = funccode + "\n\n"
        allcode += "int main(int argc, char** argv) {\n"+code+"\n}"
        return allcode
    else:
        return code
