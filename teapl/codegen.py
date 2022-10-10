from teapl.tokenizer import Token
from teapl.objects import *
from random import randint
from teapl.action import Action, ActionType, make_actions
import teapl.pretty as pretty
import teapl.expression as expr

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

def parse_code_tokenized(tokens, orig: list[Token]) -> tuple[list[Token]]:
    tokenized = pretty.pretty(tokens, orig)
    tokenized = pretty.remove_whitespaces(tokenized)
    tokenized = expr.parse_expressions(tokenized, orig)
    tokenized = expr.parse_comprasions(tokenized, orig)
    tokenized = pretty.build_funccalls(tokenized, orig)
    return tokenized

def codegen(actions: list[Action], wrap = True) -> str:
    code = ""
    funccode = ""

    variables = []

    idx = 0
    while idx < len(actions):
        el = actions[idx]  # element

        need = el.args
        if el.type == ActionType.ASSIGNATION:
            vvalue = need.value
            if isinstance(vvalue, Expression):
                vvalue = expr.expr2str(vvalue)
            else:
                vvalue = vvalue.token
            
            if "reassignation" not in el.metadata:
                vtype = to_ctype(need.type)
                vname = need.name
                code += f"{vtype} {vname} = {vvalue};\n"
                variables.append(need)
            else:
                vname = need.name
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
            mainbody = need[0][2].tokens
            mborig = need[0][2].tokens
            otherbodies = need[1:]

            maincond = [maincond.what.token, maincond.sign, maincond.with_.token]
            code += "if ("+' '.join(maincond)+") {\n"

            funcbody = parse_code_tokenized(mainbody, mborig)
            funcbody = make_actions(funcbody, mborig)
            functot = codegen(funcbody, wrap=False)

            code += functot+"}"

            for mk in otherbodies:
                if mk[0]=="else":
                    body = borig = mk[1].tokens
                    code += "else{\n"

                    funcbody = parse_code_tokenized(body, borig)
                    funcbody = make_actions(funcbody, borig)
                    functot = codegen(funcbody, wrap=False)

                    code += functot+"}"
                    break
            ...  # For elif and else

            code += "\n"
        elif el.type == ActionType.WHILE_LOOP:
            wcond = need.condition
            wbody = need.body.tokens
            worig = need.body.tokens

            maincond = [wcond.what.token, wcond.sign, wcond.with_.token]

            wbody = parse_code_tokenized(wbody, worig)
            wbody = make_actions(wbody, worig)
            
            wtot = codegen(wbody, wrap=False)

            code += "while("+' '.join(maincond)+") {\n" + \
                wtot + \
            "}\n"
        idx += 1

    if wrap:
        allcode = funccode + "\n\n"
        allcode += "int main(int argc, char** argv) {\n"+code+"\n}"
        return allcode
    else:
        return code