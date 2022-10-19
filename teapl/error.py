try:
    from teapl.tokenizer import Token
except:
    from tokenizer import Token

def crop_tabs(a):
    b = []
    for i in a:
        if isinstance(i, Token):
            if i.token == "\t": return
            else: b.append(i)
        else:
            b.append(i)
    return b

def error(tokens: list[Token], token: Token, msg: str, start: int, end: int):
    line = token.line

    seltok = []
    ffound = None # Needed first found in line to make shift start-end
    for i in tokens:
        if i.line == line:
            if ffound is None:
                ffound = i
            if i.token == "\n": continue
            seltok.append(i)
    # print(f"First: {ffound.start}, {ffound.end}, {ffound.token}")


    tokstr = ""
    for i in seltok:
        tokstr += i.token

    tokstr = tokstr.lstrip('\t')

    # print(f"{start=}; {end=}")
    # print(f"{ffound.start=}; {ffound.end=}")
    print(f"\x1b[31mError\x1b[0m: Line {line}: {msg}")
    print(f"\t{tokstr}")
    start -= ffound.start
    end -= ffound.start
    print(f"\t{' '*start}{'~'*(end-start)}")

    exit(1)
