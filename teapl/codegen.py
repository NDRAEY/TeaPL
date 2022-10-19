from random import randint

try:
    from teapl.tokenizer import Token
    from teapl.objects import *
    from teapl.action import Action, ActionType, make_actions
    from teapl.pretty import pretty, remove_whitespaces
    import teapl.expression as expr
    from teapl.utils import *
except:
    from tokenizer import Token
    from objects import *
    from action import Action, ActionType, make_actions
    from pretty import pretty, remove_whitespaces
    import expression as expr
    from utils import *

from pprint import pprint

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
    else: return typ

def find_var(variables: list, name: str):
    for i in variables:
        if i.name == name:
            return i

def simple_unite(tokens):
    a = ""

    for i in tokens:
        tmp = to_ctype(i.token)
        if tmp != i.token:
            a += tmp+" "
        else:
            a += i.token+" "

    return a

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

def format2c(value) -> str:
    if isinstance(value, Expression):
        return expr.expr2str(value)
    elif isinstance(value, Token):
        return value.token
    elif isinstance(value, Array):
        return array2c(value)
    elif isinstance(value, IndexedValue):
        return indexed2c(value)
    elif isinstance(value, FunctionCall):
        return f"{value.name}({build_args(value.args)})"
    else:
        return value

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
            
            vvalue = format2c(vvalue)

            addit = ""
            if (type(need.type) is list) and (type(need.type[1]) is list):
                addit = "[]"
            
            if "reassignation" not in el.metadata:
                # print(need.type)
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
            prepargs = build_args(prepargs)
            print("Prepargs => ", end='')
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
        elif el.type == ActionType.FUNCTION:
            fname = need.name
            fret  = to_ctype(need.return_type)
            nargs = remove_whitespaces(need.args)
            nargs = simple_unite(nargs)
            # fargs = build_args(need.args)
            fargs = nargs
            fbody = forigbody = need.tokens.tokens

            fcode = parse_code_tokenized(fbody, forigbody)
            fcode = make_actions(fcode, forigbody)
            fcode = codegen(fcode, wrap=False)

            if fret is None:
                fret = "void"
            
            # print("Name:", fname, "Return:", fret, "Args:", fargs, "Body:", fbody)

            funccode += f"{fret} {fname}({fargs}) "+"{\n" + \
                fcode + \
            "}\n"

            '''
            print("==========>")
            print(code)
            print("<==========")
            exit(1)
            '''
        elif el.type == ActionType.RETURN:
            val = need.value
            val = format2c(val)
            code += f"return {val};\n"
        elif el.type == ActionType.C_EXTERN:
            val = need.tokens

            c = ""
            for i in val:
                c += i.token

            code += c+"\n"
        else:
            print("Unimplemented actions found!")
            print(need)
            print("============================")
            exit(1)
        idx += 1

    if wrap:
        allcode = funccode + "\n\n"
        allcode += "int main(int argc, char** argv) {\n"+code+"\n}"
        return allcode
    else:
        return code
