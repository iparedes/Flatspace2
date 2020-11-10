

MT      =   1
LBL     =   2
INFO    =   3
DIST    =   4
DISPLAY =   5

OFF =   0
ON  =   1



KEYWORDS={
    'mt':MT,   # mt ident - Moves the view to the center of the object identified by ident
    'labels':LBL,
    'info':INFO,
    'dist':DIST,
    'distance':DIST,
    'disp':DISPLAY,          # DISPLAY number object - Shows info about an object in display # number
    'display':DISPLAY,
    'off':OFF,
    'on':ON

}



class Parser():

    def __init__(self):
        self.tokens=[]

    def pop(self):
        if self.tokens:
            t=self.tokens.pop(0)
        else:
            t=None
        return t

    def parse_instr(self,t):
        self.tokens=t.lower().split()
        instr=[]
        command=self.pop()
        if command in KEYWORDS.keys():
            com_code=KEYWORDS[command]
            instr.append(com_code)
            # MOVE TO
            if com_code==MT:
                ident=self.pop()
                if ident:
                    instr.append(ident)
                else:
                    instr=[]
            # LABEL
            elif com_code==LBL:
                val=self.pop()
                if val=="on" or val=="1":
                    instr.append(ON)
                else:
                    instr.append(OFF)
            # INFO
            elif com_code==INFO:
                ident=self.pop()
                if ident:
                    instr.append(ident)
                else:
                    instr=[]
            # DISTANCE
            elif com_code==DIST:
                ident1=self.pop()
                ident2=self.pop()
                if ident1 and ident2:
                    instr+=[ident1,ident2]
                else:
                    instr=[]
            # DISPLAY
            elif com_code==DISPLAY:
                disp_num=self.pop()
                ident=self.pop()
                try:
                    val=int(disp_num)
                except:
                    val=None
                if ident and val!=None:
                    instr+=[val,ident]
                else:
                    instr=[]
            elif True:
                pass
        return instr



