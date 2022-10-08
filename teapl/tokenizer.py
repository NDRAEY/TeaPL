from dataclasses import dataclass
TOKENLIST = "(){}[],.:;*+-/@#$\"\' =^~|%<>\n\t";

@dataclass
class Token:
    token: str
    start: int
    end:   int
    line:  int

def tokenize(code):
    line = 1
    tokens = []
    sptokens = []
    idx = 0

    while idx < len(code):
        i = code[idx]

        if i in TOKENLIST:
            if len(sptokens):
                tokens.append(Token(''.join(sptokens), idx-len(''.join(sptokens)), idx, line))
                sptokens = []

            if i in ("+", "-", "/", "*", "<", ">", "!", "="):
                n = code[idx+1]
                if n == "=":
                    i = i+n
                    tokens.append(Token(i, idx, idx+len(i), line))
                    idx += 2
                    continue

            if i in ("+", "-", "|", "&", "/"):
                n = code[idx+1]
                if n == i:
                    i = i+n
                    tokens.append(Token(i, idx, idx+len(i), line))
                    idx += 2
                    continue

            if i == "-" and code[idx+1] == ">":
                tokens.append(Token("->", idx, idx+2, line))
                idx += 2
                continue
            
            tokens.append(Token(i, idx, idx+len(i), line))

            if i=="\n":
                line += 1
        else:
            sptokens.append(i)
        
        idx += 1

    if len(sptokens):
        tokens.append(Token(''.join(sptokens), idx-len(''.join(sptokens)), idx, line))
        sptokens = []
    return tokens

if __name__=="__main__":
    from pprint import pprint
    pprint(tokenize("hyvaa -> huomenta"))
