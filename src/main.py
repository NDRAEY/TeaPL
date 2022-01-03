import lex
import ccode
import sys
import subprocess as sp
import time

print("The \033[31mCharmeleon\033[0m Project [v 1.0]\n")

if not sys.argv[1:]:
    print("Specify a file! Exiting...")
    exit()

code = open(sys.argv[-1]).read()
print("\rGetting ready...\033[K",end='')
starttime = time.time()
lexed = lex.code2objs(code)
ccoded = ccode.lex2ccode(lexed)
cc = ccode.CCode()
print("\rAlmost done...\033[K",end='')
codetotal = (cc.model%(cc.getnormalincs(ccoded['includes'])+"\n"+
                       ccoded['vars'],
                       ccoded['outmains'],
                       ccoded['code']))
print(codetotal)
print("\rCompiling...\033[K",end='')
gcc = sp.Popen(['gcc','-x','c','-o',sys.argv[-1].split(".")[0],'-'],stdin=sp.PIPE)
gcc.stdin.write(bytes(codetotal,'utf-8'))
gcc.stdin.close()
gcc.wait()
print("\rDone %.2fs\033[K\n"%(time.time()-starttime),end='')
