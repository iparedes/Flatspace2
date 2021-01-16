from fspace import *

DATA_FILE="data3"

class Juego:
    def __init__(self):
        self.SS=SSystem()

        self.max_peri=0
        self.max_apo=0

        self.load_data()


    def load_data(self):
        file1 = open(DATA_FILE, 'r')
        Lines = file1.readlines()
        lastPlanet=None
        for l in Lines:
            l.strip()
            if l[0] != '#':
                l.rstrip()
                items = l.split(',')
                #removes spaces from names
                items[1]=items[1].strip()
                if items[0] == "Sun":
                    self.SS.Sol.name=items[0]
                    self.SS.Sol.mass = float(items[1])
                    self.SS.Sol.radius = float(items[2])
                    self.SS.Sol.pos = Pos(0, 0)
                elif items[0] == "*": # Satellite
                    name=items[1]
                    mass=float(items[2])
                    radius = float(items[3])
                    peri = float(items[4])
                    apo = float(items[5])
                    incl = float(items[6])
                    pos = float(items[7])
                    s=Planet(lastPlanet,name,mass,radius,peri,apo,incl,pos)
                    lastPlanet.add_satellite(s)
                elif items[0] == "&": # ship
                    name=items[1]
                    mass=float(items[2])
                    x = float(items[3])
                    y = float(items[4])
                    xvel = float(items[5])
                    yvel = float(items[6])
                    vel=Vector(x=xvel,y=yvel)

                    pos=Pos(x,y)
                    s=Ship(name,mass,pos,vel)
                    self.SS.add_ship(s)
                else:
                    name=items[0]
                    mass=float(items[1])
                    radius = float(items[2])
                    peri = float(items[3])
                    apo = float(items[4])
                    incl = float(items[5])
                    pos = float(items[6])
                    if apo>self.max_apo:
                        self.max_apo=apo
                        self.max_peri=peri
                    #self.SS.add_planet(name,mass,radius,peri,apo,incl,pos)
                    P=Planet(self.SS.Sol,name,mass,radius,peri,apo,incl,pos)
                    lastPlanet=P
                    self.SS.Sol.add_planet(P)



if __name__ == '__main__':
    J=Juego()
    print(J.SS.ships[0].primary)
