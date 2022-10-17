from random import randint

try:
    from teapl.tokenizer import Token
    from teapl.objects import *
    from teapl.action import Action, ActionType, make_actions
    import teapl.pretty as pretty
    import teapl.expression as expr
except:
    from tokenizer import Token
    from objects import *
    from action import Action, ActionType, make_actions
    import pretty as pretty
    import expression as expr

from pprint import pprint

def randstr() -> str:
    return ''.join([chr(randint(ord('a'), ord('z'))) for t in range(10)])

def to_ctype(typ: str) -> str:
    if type(typ) is list:
        typ = typ[0]
    if typ=="ubyte": return "unsigned char"
    elif typ=="byte": return "char"
    elif typ=="ushort": return "unsigned short"
    elif typ=="short": return "short"
    elif typ=="uint": return "unsigned int"
    elif typ=="int": return "int"
    elif typ=="string": return "char*"
    elif typ=="bool": return "char"

def indexed2c(val: IndexedValue) -> str:
    # TODO: Slices
    return val.value.token + "["+val.index.tokens[0].token+"]"

def build_args(variables: list[Variable], args: list[Token]) -> str:
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

        if n+1 < len(prep):
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
    tokenized = pretty.build_arrays(tokenized, orig)
    tokenized = pretty.build_indexes(tokenized, orig)
    tokenized = pretty.build_funccalls(tokenized, orig)
    return tokenized

def parse_code_tokenized_lite(tokens, orig: list[Token]) -> tuple[list[Token]]:
    tokenized = pretty.pretty(tokens, orig)
    tokenized = pretty.remove_whitespaces(tokenized)
    tokenized = expr.parse_expressions(tokenized, orig)
    tokenized = pretty.build_arrays(tokenized, orig)
    tokenized = pretty.build_indexes(tokenized, orig)
    tokenized = pretty.build_funccalls(tokenized, orig)
    return tokenized

def array2c(array: Array):
    s = ""
    elements = []

    for i in array.tokens:
        if i.token == ",": continue
        elements.append(i)

    s += "{"
    for n, i in enumerate(elements):
        if n == len(elements)-1:
            s += i.token
        else:
            s += i.token+", "
    s += "}"
    return s

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
            elif isinstance(vvalue, Token):
                vvalue = vvalue.token
            elif isinstance(vvalue, Array):
                vvalue = array2c(vvalue)
            elif isinstance(vvalue, IndexedValue):
                vvalue = indexed2c(vvalue)

            addit = ""
            if (type(need.type) is list) and (type(need.type[1]) is list):
                addit = "[]"
            
            if "reassignation" not in el.metadata:
                print(need.type)
                vtype = to_ctype(need.type[0]) if type(need.type) is list else to_ctype(need.type)
                vname = need.name
                code += f"{vtype} {vname}{addit} = {vvalue};\n"
                variables.append(need)
            else:
                vname = need.name
                code += f"{vname} = {vvalue};\n"
                variables.append(need)

        elif el.type == ActionType.FUNC_CALL:
            fname = need.name
            fargs = argsorig = need.args

            prepargs = parse_code_tokenized_lite(fargs, argsorig)
            prepargs = build_args(variables, prepargs)
            print("Prepargs")
            pprint(prepargs)

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
