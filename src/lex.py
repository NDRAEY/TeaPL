import re
from pprint import pprint
import os
from errors import *

VARS = {}
root = {}

class RegExp:
    func = re.compile(r"func\ *(?P<fname>\w*)\((?P<args>[\W\w]([^\)]|[^\)\ ])*)\)*\{")
    func_z = re.compile(r"func\ *(?P<fname>\w*)\((?P<args>[\W\w][^\)]*)\)*\{")
    if_ = re.compile(r"if.*?\((?P<cond>[\w\W].*?\)).*?\{")
    var_nonum = r"(\+|\-|\/|\*|)\="
    funccall = re.compile(r"(?P<fname>.*?)\((?P<args>.*?)\)(.|)$")
    use = re.compile(r"use[\ {}]*(?P<mname>.*?$)")
    comment = re.compile(r"^.*?#")

code = '''
afim = 0
brake = 4+7
cplusplus =999
double revol = 63
brake = 1
eba = 'Hello'
afim+=1

func hello(Var1 net, Var2 dry){
    print("Hello");
    if(afim==0) {
        print("Afim is 0!")
    }
}
func eploy(){
    pri5n()
}
func dep(){
    ttt(drobes, hahah)
}
if(e>0){
    eprog()
}
if (j>1) {
    ddr()
}

if(n==1){ hello() }
func empty(){}
func empty(){}

if(afim==0){
    hello()
}

print("Call from main();")

'''

def fixline(ln):
    while None in ln:
        ln.remove(None)
    while '' in ln:
        ln.remove('')
    for i in ln:
        modif = i
        if modif[0]==' ':
            modif=modif[1:]
        if modif[-1]==' ':
            modif=modif[:-1]
        ln[ln.index(i)]=modif
    return ln

def fixargs(c):
    if ")" in c:
        t = list(c)
        del t[t.index(")")]
        return ''.join(t)
    else:
        return c

def fnameclean(a):
    if len(a)==0: return a
    e = list(a)
    while (e[0]==";" or e[0]==" "):
        del e[0]
    a = ''.join(e)
    return a

def code2objs(code: str):
    stk = []
    codesp = code.split("\n")
    fnstk = []
    line = 0
    while line<len(codesp):
        if ('=' in codesp[line]) and (not ("if" in codesp[line])): # Maybe Variable assignation
            nd = fixline(re.split(RegExp.var_nonum,codesp[line]))
            if nd[0] in VARS:
                whereis = codesp[line].index('=')
                modiftype = codesp[line][whereis-1:whereis]
                stk.append({
                    'type':'reassignation',
                    'variable':nd[0],
                    'value':nd[1 if modiftype==" " else 2],
                    'modifer':modiftype if modiftype!=" " else None
                })
                line+=1
                continue
            VARS[nd[0]]=nd[1]
            stk.append({
                'type': 'assignation',
                'variable': nd[0].split(" ")[1] if len(nd[0].split(" "))==2 else nd[0],
                'value': nd[1],
                'dtype':nd[0].split(" ")[0] if len(nd[0].split(" "))==2 else None
            })
        elif codesp[line].startswith('func'):
            fnstk=[]
            fl=0
            fnflows=[]
            cnt = 0
            for i in codesp[codesp.index(codesp[line]):]:
                if '{' in i: cnt+=1
                if '}' in i: cnt-=1
                fl+=1
                fnstk.append(i)
                if cnt==0: break
            mtch = RegExp.func_z.match('\n'.join(fnstk))
            fname = mtch.group("fname")
            args = fixargs(mtch.group("args")).split(",")
            for i in args:
                nz = list(i);
                if len(nz)==0: break
                while nz[0]==" ":
                    del nz[0]; 
                args[args.index(i)]=''.join(nz)
            body = '\n'.join(fnstk)
            body = body[body.index("{"):]
            while '' in args: args.remove('')
            for arg in args:
                parm = arg.split(" ")
                if len(parm)<2:
                    SyntaxError(line,"Type of argument not given.",
                    codesp[line],codesp[line].index(arg),len(" ".join(parm))-1)
            stk.append({
                'type':'funcassign',
                'fname':fname,
                'args':args,
                'body':code2objs(body[1:-1])
            })
            line+=fl-1
        elif ''.join(codesp[line])=='':
            line+=1
            continue
        elif ("if") in codesp[line]:
            ifstk = []
            fl = 0
            cnt = 0
            for i in codesp[codesp.index(codesp[line]):]:
                if '{' in i: cnt+=1
                if '}' in i: cnt-=1
                fl+=1
                ifstk.append(i)
                if cnt==0: break
            mtch = RegExp.if_.match(fnameclean('\n'.join(ifstk)))
            body = '\n'.join(ifstk)
            body = code2objs(body[body.index("{")+1:-1])
            stk.append({
                'type':'if',
                'c':mtch.group("cond"),
                'body':body
            })
            line+=fl-1
        elif RegExp.funccall.match(codesp[line]):
            rg = RegExp.funccall.findall(codesp[line])
            for r in rg:
                fname = fnameclean(r[0])
                args = r[1]
                stk.append({
                    'type':'funccall',
                    'fname':fname,
                    'args':[fnameclean(e) for e in args.split(",")]
                })
        elif RegExp.use.match(codesp[line]):
            rg = RegExp.use.match(codesp[line])
            mname = rg.group("mname")
            if not os.path.isfile(mname):
                ModuleError(line,"Not module found: %s"%mname)
            stk.append({
                'type':'import',
                'module':open(mname).read() # should be imported in stage 2
            })
        elif RegExp.comment.match(codesp[line]):
            pass
        else:
            print("OTHER: "+codesp[line])
        line+=1
    return stk

def lexobjs(objs: dict):
    pass

if __name__ == "__main__":
    print(code2objs(code))
