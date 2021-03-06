import sys
import logging
from view import *
from display import *
from geometry import *
from fspace import *
from parser import *
from console import *
import pygame as pg

#todo needs logging badly

#todo difference between primary and SOI body


DATA_FILE='data'

ZOOM_FACTOR = 25
MOVE_FACTOR = 10

# The time rate is multiplied by the dt
# the dt are milliseconds calculated dividing one second between the FPS
TIME_RATE=[0,100,1000,10000,1e5,1e6,1e7,1e8]
FPS = 10

logging.basicConfig(filename='fspace.log', level=logging.DEBUG)

class Game(object):
    def __init__(self):
        self.done = False
        self.SS=SSystem()
        self.SSProjection=None


        self.max_apo=0
        self.max_peri=0 # watchout that max_peri is not the biggets periapsis, but the pri corresponding to max_apo
        self.load_data()
        self.clock = pg.time.Clock()
        self.Display = Display(1024)

        self.parser=Parser()
        self.console=Console(self.Display.WIDTH,self.Display.HEIGHT)


        #o=self.SS.find("bolo")
        #for i in self.SS.Sol:
        #    print(i.name)

        # sets the view with the sun in the center to accommodate to see complete the largest orbit
        # it is not totally correct as it assumes that the orbit is horizontal in the ref. coords

        # Ojo here. Only for data3 ##########
        #self.max_apo=1e8
        #####################################

        self.View=View(self.Display,width=(self.max_apo*2.05))
        #remove **********************************
        self.View = View(self.Display, width=1e12)
        center=Pos(0,0)
        pos_display=self.View.trans(center)
        self.Display.draw_point(pos_display)

        self.time_rate_index=0
        self.projection=False
        # This is only for testing purposes. The parent of the orbit should be the Sun, not the planet
        # P=Planet("test",1e9,6e6,Pos(5e6,5e6))
        # O=Orbit(0.47E+11, 9.52E+11,30)
        # O.body=P
        # self.View.draw_planet(P)
        # self.View.draw_orbit(O)

    # returns True if point inside rect
    # rect is pg.Rect, point is a (x,y) tuple
    def is_inside(self,rect,point):
        x=point[0]
        y=point[1]
        if (rect.left<=x<=rect.right) and (rect.top<=y<=rect.bottom):
            return True
        else:
            return False

    def update_time_rate(self):
        self.time_rate_index+=1
        if self.time_rate_index==len(TIME_RATE):
            self.time_rate_index=1
        #print("Time rate index: "+str(self.time_rate_index))

        milispertick=1000/FPS
        deltasecs=(milispertick/1000)*TIME_RATE[self.time_rate_index]
        #print("Delta per tick: "+str(deltasecs))

    def exec(self,t):
        instr=self.parser.parse_instr(t)
        if instr:
            cmd=instr.pop(0)
            # MOVE TO
            if cmd==MT:
                ident=instr.pop(0)
                obj=self.SS.find(ident)
                if obj:
                    pos=obj.pos
                    self.View.set_center(pos)
            # LABEL
            elif cmd==LBL:
                val=instr.pop(0)
                if val==ON:
                    self.View.labels=True
                else:
                    self.View.labels=False
            # INFO
            elif cmd==INFO:
                ident=instr.pop(0)
                obj=self.SS.find(ident)
                if obj:
                    print(str(obj))
            # DISTANCE
            elif cmd==DIST:
                id1=instr.pop(0)
                id2 = instr.pop(0)
                obj1=self.SS.find(id1)
                obj2 = self.SS.find(id2)
                if obj1 and obj2:
                    p1=obj1.pos
                    p2=obj2.pos
                    d=p1.distance(p2)
            elif cmd==DISPLAY:
                dispnum=instr.pop(0)
                id=instr.pop(0)
                obj=self.SS.find(id)
                if obj:
                    info=obj.__str__
                    self.Display.info_box[dispnum]=info

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
                    logging.debug("Adding ship "+s.name)
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


    def draw(self, system):
        #self.Display.screen.fill((0, 0, 0))
        self.console.draw(self.Display.screen)
        self.Display.draw_info_boxes()

        bodies=iter(system.Sol)
        # the first element of the iterator is the Sun
        body=next(bodies)
        if self.View.in_view(body):
            self.View.draw_sun(body)
        for body in bodies:
            if self.View.in_view(body):
                self.View.draw_planet(body)
            if self.View.area.overlap(body.orbit.area):
                self.View.draw_orbit(body.orbit)

        for s in system.ships:
            if self.View.in_view(s):
                self.View.draw_ship(s)

        # if self.View.in_view(self.SS.Sol):
        #     self.View.draw_sun(self.SS.Sol)
        # # this does not draw satellites if the planet is not in view
        # for p in self.SS.Sol.satellites:
        #     if self.View.in_view(p):
        #         self.View.draw_planet(p)
        #     # draw orbit
        #     if self.View.area.overlap(p.orbit.area):
        #         self.View.draw_orbit(p.orbit)
        #     for s in p.satellites:
        #         if self.View.in_view(p):
        #             self.View.draw_satellite(s)
        #         if self.View.area.overlap(s.orbit.area):
        #             self.View.draw_orbit(s.orbit)


    # Handles events
    def event_loop(self):
        events=pg.event.get()
        #for event in events:
        while events:
            event=events.pop(0)
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.KEYDOWN:
                if self.console.active:
                    events.insert(0,event)
                    ret=self.console.update(events)
                    if ret:
                        # pressed enter
                        t=self.console.get_text()
                        self.exec(t)
                    #break
                else:
                    if event.key == pg.K_LEFT:
                        self.View.move(-MOVE_FACTOR, 0)
                    if event.key == pg.K_RIGHT:
                        self.View.move(MOVE_FACTOR, 0)
                    if event.key == pg.K_UP:
                        self.View.move(0,MOVE_FACTOR)
                    if event.key == pg.K_DOWN:
                        self.View.move(0,-MOVE_FACTOR)
                    if event.key == pg.K_z:
                        self.View.zoom(ZOOM_FACTOR)
                    if event.key == pg.K_x:
                        self.View.zoom(-ZOOM_FACTOR)
                    # t: move to next time rate
                    if event.key == pg.K_t:
                        self.update_time_rate()
                    # f: Projection
                    if event.key == pg.K_f:
                        self.projection=not self.projection
                    if event.key == pg.K_p:
                        if self.time_rate_index!=0:
                            self.time_rate_index=0
                            logging.info('Pausing')
                        else:
                            self.time_rate_index = 1
                            logging.info('Set time rate '+str(TIME_RATE[self.time_rate_index]))
            elif event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                if self.console.area.collidepoint(pos[0],pos[1]):
                    self.console.active=True
                else:
                    self.console.active=False



# En cada tick se actualiza el sistema.
# A 10 FPS el sistema se actualiza 10 veces por segundo, por tanto, el delta es 100ms
# tomamos esto como Time_rate x1, el valor que pasamos al update en segundos es el delta/1000 (0.1s)
# Time_rate x10 el valor al delta es 1s cada tick
# en general el valor para el update es (delta/1000)*Time_rate

    def run(self):
        tix=0
        while not self.done:
            # we do this here instead inside draw to not overwrite the projections
            self.Display.screen.fill((0, 0, 0))
            self.event_loop()

            # updates the clock once per second, regardless the speed
            tix+=self.clock.tick(FPS)
            if tix>=1000:
                tix=0
                self.Display.draw_clock(self.SS.epoch)
            else:
                self.Display.draw_clock()
            # instead of getting the ticks from clock.tick. I assume it works fine and calculate directly
            # mmmmm, doesn't look right
            self.dt = 1000/FPS # milliseconds per frame
            self.dt *= TIME_RATE[self.time_rate_index]
            self.dt /=1000 # convert to seconds

            if self.time_rate_index!=0:
                self.SS.update(self.dt)

            self.draw(self.SS)
            pg.display.update()

        pg.quit()
        sys.exit()
