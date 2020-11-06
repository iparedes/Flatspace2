

MT  =   1
LBL =   2

OFF =   0
ON  =   1



KEYWORDS={
    'mt':MT,   # mt ident - Moves the view to the center of the object identified by ident
    'labels':LBL,
    'off':OFF,
    'on':ON

}



class Parser():

    def __init__(self):
        self.tokens=[]


    def parse_instr(self,t):
        tokens=t.lower().split()
        instr=[]
        command=tokens.pop(0)
        if command in KEYWORDS.keys():
            com_code=KEYWORDS[command]
            instr.append(com_code)
            if com_code==MT:
                ident=tokens.pop(0)
                if ident:
                    instr.append(ident)
                else:
                    instr=[]
            elif com_code==LBL:
                val=tokens.pop(0)
                if val=="on" or val=="1":
                    instr.append(ON)
                else:
                    instr.append(OFF)
            elif True:
                pass

        return instr



