import re
import subprocess as sp
import os, stat, errors

D_QUOTE = '\"'
S_QUOTE = "\'"
MATHSPLIT = r"(\+|\-|\/|\*)"

class CCode:
    def __init__(self):
        self.model = '''%s
%s
int main(int argc, char **argv) {
%s
return 0;
}

'''
        self.code = ""
        self.includes = []
        self.vars = ""
        self.outmains = ""
        self.root = {
            'print':{
                'cfname':'printf',
                'cbody':'printf(!!)',
                'needs':'<stdio.h>'
            }
        }
    def addbefore(self,codes):
        self.model=codes+"\n"+self.model

    def define(self,dname,value):
        self.addbefore("#define %s %s"%(dname,str(value)))

    def include(self,lib,local=False):
        qut = ["<",">"] if not local else ['"','"']
        self.addbefore("#include %s%s%s"%(qut[0],lib,qut[-1]))
        self.includes.append(qut[0]+lib+qut[-1])

    def alldigits(self,s):
        return all([a.isdigit() for a in s])

    def isstring(self,s):
        return ((s[0]=='\"') and (s[-1]=='\"')) or ((s[0]=="\'") and (s[-1]=="\'"))

    def rng(self,intz,fr,to):
        return (intz>=fr and intz<=to)

    def malloc(self,hm:int,ty=None):
        if not "stdlib.h" in self.includes:
            self.include("stdlib.h")
        return ("("+ty+" )" if ty else " ")+"malloc(%d);"%hm

    def hasfp(self,s):
        return "." in s

    def gettype(self,lxm):
        if self.hasfp(lxm) and (not self.isstring(lxm)) and (not lxm[0]=="\""):
            wrk = float(lxm)
            if self.rng(wrk,1.2e-38,3.4e+38):
                typ = "float"
            elif self.rng(wrk,2.3e-308,1.7e+308):
                typ = "double"
            return typ
        
        if self.alldigits(lxm): # Exactly number
            wrk = float(lxm)
            if self.rng(wrk,-128,127):
                typ = "signed char"
            elif self.rng(wrk,0,255):
                typ = "unsigned char"
            elif (self.rng(wrk,-32768,32767)):
                typ = "short"
            elif (self.rng(wrk,-2147483648,2147483647)):
                typ = "int"
            elif (self.rng(wrk,0,65535)):
                typ = "unsigned short"
            elif self.rng(wrk,0,4294967295):
                typ = "unsigned int"
            elif (self.rng(wrk,-9223372036854775808,9223372036854775807)):
                typ = "long"
            elif (self.rng(wrk,0,18446744073709551615)):
                typ = "unsigned long"
            return typ
        else:
            if lxm[0]==D_QUOTE and lxm[-1]==D_QUOTE:
                e = lxm[1:-1]
                if len(e)==1:
                    typ = "char"
                if len(e)>1:
                    typ = "char*"
                return typ
            else:
                slashed = re.split(MATHSPLIT,lxm)
                slashedwhere = re.search(MATHSPLIT,lxm)
                slashedwhere = lxm[slashedwhere.start()] if slashedwhere else None
                if slashed: lxm=slashed[0]
                print(lxm, len(lxm))
                if lxm[0]==D_QUOTE and (not lxm[-1]==D_QUOTE):
                    err = errors.Error("SYNTAX [2nd stage]",
                                       0,
                                       "Unclosed string statement [left QUOTE]\n\n"+lxm+"\n"+("~"*(len(lxm)))+"^"
                                       ); err.error()
                elif (not lxm[0]==D_QUOTE) and lxm[-1]==D_QUOTE:
                    err = errors.Error("SYNTAX [2nd stage]",
                                       0,
                                       "Unclosed string statement [right QUOTE]\n\n"+lxm+"\n"+"^"+("~"*(len(lxm)-1))
                                       ); err.error()
                else:
                    print("DBG: Objects and arrays not supported")
                #exit(1)

    def addcodeline(self,line):
        self.code+=line+"\n"

    def addvarline(self,line):
        self.vars+=line+"\n"

    def addoutmains(self,line):
        self.outmains+=line+"\n"

    def getnormalincs(self,incs):
        a = ""
        for i in incs:
            a+="#include "+i+"\n"
        return a

    def getcode(self):
        return self.model%(self.vars,self.outmains,self.code)

    def buildvar(self,typ,name,val):
        typ = self.gettype(val) if not typ else typ
        return "%s %s = %s;"%(typ,name,str(val))

    def buildrevar(self,name,val,modifer=None):
        return "%s %s= %s;"%(name,"" if not modifer else modifer,str(val))

    def getcode_nosnip(self):
        return (self.outmains+"\n"+self.vars+"\n"+self.code)

    def compile(self,out="main"):
        compiler = sp.Popen(["gcc","-x","c","-o",out,"-"],stdin=sp.PIPE)
        compiler.stdin.write(bytes(self.getcode(),'utf-8'))
        compiler.stdin.close()

def lexremts(a): # Remove redundant \t<s>
    e = list(a)
    while e[0]=='\t': del e[0]
    return ''.join(e)

def lex2ccode(objs):
    cc = CCode()
    for i in objs:
        if i['type']=="assignation":
            if i['dtype']==None:
                dtype = cc.gettype(i['value'])
            else:
                dtype = i['dtype']
            vname = i['variable']
            slashed = re.split(MATHSPLIT,i['value'])
            slashedwhere = re.search(MATHSPLIT,i['value'])
            slashedwhere = i['value'][slashedwhere.start()] if slashedwhere else None
            if slashedwhere:
                #slashed.remove(slashedwhere)
                tmp = []
                for n in slashed:
                    if cc.isstring(n):
                        tmp.append({'value':n,'type':'string'})
                    elif cc.alldigits(n) or (cc.hasfp(n) and not (cc.isstring(n))):
                        tmp.append({'value':n,'type':'number'})
                    else:
                        tmp.append({'value':n,'type':'arith'})
                #print("TMP!: "+str(tmp))
                glen = 0
                mlcsz = 256
                cc.addcodeline("char* "+vname+" = "+cc.malloc(256,"char*"))
                cc.addcodeline("strcpy("+vname+","+tmp[0]['value']+");")
                glen+=len(tmp[0]['value'])
                del tmp[0]
                lastsign = None
                lasttype = tmp[0]['type']
                for i in tmp:
                    ity = i['type']
                    iva = i['value']
                    if ity=="string":
                        #if glen>mlcsz:
                        #cc.addcodeline(cc.realloc(""))
                        cc.addcodeline("strcat("+vname+","+i['value']+");")
                        glen+=len(tmp[0]['value'])
                    elif cc.alldigits(iva) or (cc.hasfp(iva) and not (cc.isstring(iva))):
                        err = errors.Error("TYPE [2nd stage]", 0,
                                           "Cannot concatenate number to string...\n\n"); err.error()
                    elif ity=="arith":
                        if lasttype=="string":
                            match lastsign:
                                case "-":
                                    errors.Error("TYPE [2nd stage]", 0,
                                                 "Cannot '-' from string...\n").error()
                            
                        lastsign=iva
                    lasttype=ity
                tmp=[]
            else:
                #print(dtype,vname,i['value'])
                cc.addvarline(cc.buildvar(dtype,vname,i['value']))
        elif i['type']=="reassignation":
            slashed = re.split(MATHSPLIT,i['value'])
            slashedwhere = re.search(MATHSPLIT,i['value'])
            slashedwhere = i['value'][slashedwhere.start()] if slashedwhere else None
            tmp = []
            if slashed:
                for e in slashed:
                    if cc.isstring(e):
                        tmp.append({'value':e,'type':'string'})
                    elif cc.alldigits(e) or (cc.hasfp(e) and not (cc.isstring(e))):
                        tmp.append({'value':e,'type':'number'})
                    else:
                        tmp.append({'value':e,'type':'variable'})
                print("RETMP: "+str(tmp))
            cc.addcodeline(cc.buildrevar(i['variable'],i['value'],i['modifer']))
        elif i['type']=="funcassign":
            args = ", ".join(i['args'])
            fname = i['fname']
            body = i['body']
            esp = lex2ccode(body)
            print("LEX2CCODE: "+str(esp))
            cc.addoutmains("void %s(%s){%s}"%(fname,args,esp['vars']+"\n"+esp['code']))
            
        elif i['type']=="funccall":
            fname = lexremts(i['fname'])
            args = ', '.join(i['args'])
            if fname in cc.root:
                needs = cc.root[fname]['needs']
                fname = cc.root[fname]['cfname']
                if needs and not (needs in cc.includes):
                    cc.include("stdio.h")
            cc.addcodeline("%s(%s);"%(fname,args))
    return {'includes':cc.includes,'vars':cc.vars,'code':cc.code,'outmains':cc.outmains}

if __name__=="__main__":
    c = CCode()
    c.define("PIKACHU_VER",'\"1.0\"')
    c.printf(r"Hello, Valera!\n")
    c.printf(r"Goodbye, Valera!\n")
    print(c.buildvar("friend",'"charmeleon"'))
