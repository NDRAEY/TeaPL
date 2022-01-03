class Error:
    def __init__(self,type,line,descr):
        self.header="\033[31m%s ERROR\033[0m at line \033[33m%d\033[0m: %s"%(type,line,descr)
    def error(self):
        print(self.header)
        exit(1)
    def error_noexit(self):
        print(self.header)

def ModuleError(ln,z):
    err = Error("MODULE",ln,z)
    err.error()

def SyntaxError(ln,z,lineraw=None,where=None,l=None):
    err = Error("SYNTAX",ln,z)
    err.error_noexit()
    if lineraw:
        print("\n"+lineraw)
    if where:
        print(" "*where,end=''); print("^",end='')
    if l:
        print("~"*l)
    print("")
    exit(1)
