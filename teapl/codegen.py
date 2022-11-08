from random import randint

try:
    from teapl.tokenizer import Token
    from teapl.objects import *
    from teapl.action import Action, ActionType, make_actions
    from teapl.pretty import pretty, remove_whitespaces, build_arrays
    import teapl.expression as expr
    from teapl.utils import *
except:
    from tokenizer import Token
    from objects import *
    from action import Action, ActionType, make_actions
    from pretty import pretty, remove_whitespaces, build_arrays
    import expression as expr
    from utils import *

from pprint import pprint

def to_ctype(typ: str) -> str:
    arr = False
    if type(typ) is list:
        typ = typ[0]
        arr = True

    if typ=="ubyte":    my = "unsigned char"
    elif typ=="byte":   my = "char"
    elif typ=="ushort": my = "unsigned short"
    elif typ=="short":  my = "short"
    # elif typ=="uint":   my = "unsigned int"
    elif typ=="int":    my = "int"
    elif typ=="string": my = ["char", []]
    elif typ=="bool":   my ="char"
    else: my = typ

    if arr:
        my = [my, []]

    return my

def to_ctype2(typ):
    if type(typ) is list:
        return typ[0]+"[]"
    else:
        return typ

def find_var(variables: list, name: str):
    for i in variables:
        if i.name == name:
            return i

def simple_unite(tokens):
    '''
    a = ""

    for i in tokens:
        tmp = to_ctype(i.token)
        if tmp != i.token:
            a += tmp+" "
        else:
            a += i.token+" "

    return a
    '''

    '''
    st = ""
    tmp = []

    idx = 0
    while idx < len(tokens):
        el = tokens[idx]

        typ = el.token
        idx += 1

        var = []
        while True:
            if (idx >= len(tokens)) or tokens[idx].token == ",": break
            var.append(tokens[idx].token)
            idx += 1
        print(var)
        if var:
            tmp.append([typ, var[0]])
        else:
            tmp.append(typ)
        idx += 1
    print(1, tmp)

    newtmp = []

    idx = 0
    while idx < len(tmp):
        if len(tmp[idx])==1:
            if idx-1 < 0: # a, b, c  # should be: type a, b, c
                print("No type for first argument!!!")
                exit(1)
            newtmp[idx-1].append(tmp[idx])
            del tmp[idx]
            continue
        else:
            newtmp.append(tmp[idx])
        idx += 1
    print(2, newtmp)

    for q in newtmp:
        t = to_ctype(q[0])
        v = q[1:]

        if type(t) is list:
            for n, _ in enumerate(v):
                v[n] += "[]"
            t = t[0]
            

        for k in v:
            st += t+" "+k+", "
        
    st = st[:-2]

    print(st)

    # exit(1)
    
    return st
    '''

    tokens = build_arrays(tokens, tokens)
    idx = 0

    total = []

    while idx < len(tokens):
        el = tokens[idx]

        built = []
        while True:
            if idx >= len(tokens): break
            if isinstance(tokens[idx], Token):
                if tokens[idx].token == ",": break
                built.append(tokens[idx].token)
            elif isinstance(tokens[idx], Array):
                built[-1] = [built[-1], []]
            idx += 1
        
        total.append(built)
        idx += 1

    if len(total[0]) <= 1:
        print(f"No type for first argument: {total[0][0]}")
        exit(1)

    newtotal = []
    idx = 0
    while idx < len(total):
        if len(total[idx]) == 1:
            if type(total[idx]) is list:
                newtotal[idx-1].extend(total[idx])
            else:
                newtotal[idx-1].append(total[idx])
            del total[idx]
            continue
        else:
            newtotal.append(total[idx])
        idx += 1

    idx = 0
    string = ""

    while idx < len(newtotal):
        el = newtotal[idx]

        iw = 0
        while iw < len(el[1:]):
            # print(el[0], to_ctype(el[0]))
            t = to_ctype(el[0])

            if type(t) is list:
                string += t[0] + " " + el[iw+1] + "[], "
            else:
                string += t + " " + el[iw+1] + ", "
            iw += 1
            
        idx += 1

    string = string[:-2]

    print(string)
    return string

def array2c(array: Array):
    s = ""
    elements = []

    for i in array.tokens:
        if isinstance(i, Token) and (
            i.token == "," \
            or i.token == "\n" \
            or i.token == "\t" 
        ): continue
        elements.append(i)

    s += "{"
    for n, i in enumerate(elements):
        if n == len(elements)-1:
            if isinstance(i, Token):
                s += i.token
            elif isinstance(i, Array):
                s += array2c(i)
            else:
                print("Unknown type!!!")
                exit(1)
        else:
            if isinstance(i, Token):
                s += i.token+", "
            elif isinstance(i, Array):
                s += array2c(i)+", "
            else:
                print("Unknown type!!!")
                exit(1)
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

def dummy_array_filter(array: Array):
    '''
    n = []

    for i in array.tokens:
        if isinstance(i, Array):
            n.append(i)

    return n
    '''
    return [i for i in array.tokens if not (isinstance(i, Token) and \
            (i.token=="," or i.token=="\n" or i.token=="\t"))]

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
            isarray = False

            addit = ""
            if (type(need.type) is list) and (type(need.type[1]) is list):
                # print("!!!", need, "ARRAY LENGTH", len(dummy_array_filter(need.value)))
                arrlen = len(dummy_array_filter(need.value))

                # print("+++++++++++ BEFORE")
                # pprint(need.value)
                # print("+++++++++++ AFTER")
                tmp = Array(dummy_array_filter(need.value))
                pprint(tmp)
                while True:
                    # print("!!!!!!!!")
                    # pprint(tmp)
                    # print("!!!!!!!!")
                    if isinstance(tmp, Array):
                        addit += f"[{len(dummy_array_filter(tmp))}]"
                        tmp = tmp.tokens[0]
                    else:
                        break
                isarray = True
            
            if "reassignation" not in el.metadata:
                # print(need.type)
                vtype = to_ctype(need.type[0]) if type(need.type) is list else to_ctype(need.type)
                if type(vtype) is list:
                    # addit = "[]"
                    vtype = vtype[0]
                    if isarray: vtype+="*"

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
            # print("Pre-Prepargs => ", end='')
            # pprint(prepargs)
            prepargs = build_args(prepargs)
            # print("Prepargs => ", end='')
            # pprint(prepargs)

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
                    # break
                elif mk[0]=="elif":
                    elifcond = mk[1]
                    body = borig = mk[2].tokens
                    code += "else if("+' '.join([elifcond.what.token, elifcond.sign, elifcond.with_.token])+") {\n"

                    funcbody = parse_code_tokenized(body, borig)
                    funcbody = make_actions(funcbody, borig)
                    functot = codegen(funcbody, wrap=False)

                    code += functot+"}"
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
