import sys
from view import *
from display import *
from geometry import *
from fspace import *
import pygame as pg
import pygame_textinput

DATA_FILE='data'

ZOOM_FACTOR = 25
MOVE_FACTOR = 10

# The time rate is multiplied by the dt
# the dt are milliseconds calculated dividing one second between the FPS
# the default time rate (1) are 100ms per update
TIME_RATE=[0,1,10,100,1000,10000,1e5,1e6]
FPS = 10

CONSOLE_MARGIN=10

class Game(object):
    def __init__(self):
        self.done = False
        self.SS=SSystem()

        self.max_apo=0
        self.max_peri=0 # watchout that max_peri is not the biggets periapsis, but the pri corresponding to max_apo
        self.load_data()
        self.clock = pg.time.Clock()
        self.Display = Display(1024)

        self.console=pygame_textinput.TextInput(initial_string="",font_size=14,text_color=(255,255,255))
        self.console_active=False
        self.console_area=pg.Rect(CONSOLE_MARGIN,self.Display.HEIGHT-self.console.font_size,self.Display.WIDTH-(CONSOLE_MARGIN*2),self.console.font_size)
        # sets the view with the sun in the center to accommodate to see complete the largest orbit
        # it is not totally correct as it assumes that the orbit is horizontal in the ref. coords

        # Ojo here. Only for data3 ##########
        #self.max_apo=1e8
        #####################################

        self.View=View(self.Display,width=(self.max_apo*2.05))
        #self.View = View(self.Display, width=800)
        center=Pos(0,0)
        pos_display=self.View.trans(center)
        self.Display.draw_point(pos_display)

        self.time_rate_index=0

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

    def load_data(self):
        file1 = open(DATA_FILE, 'r')
        Lines = file1.readlines()
        lastPlanet=None
        for l in Lines:
            l.strip()
            if l[0] != '#':
                l.rstrip()
                items = l.split(',')
                if items[0] == "Sun":
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
                    # todo add velocity vector in ship constructor
                    s=Ship(self.SS.Sol,name,mass,Pos(x,y),vel)
                    self.SS.ships.append(s)
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


    def draw(self):
        self.Display.screen.fill((0, 0, 0))
        pg.draw.rect(self.Display.screen,(16,16,16),self.console_area)
        self.Display.screen.blit(self.console.get_surface(), (self.console_area.left,self.console_area.top))
        # remove *************
        #self.Display.draw_line_cartesian(Pos(self.View.area.left, 0), Pos(self.View.area.right, 0), self.View.area)
        if self.View.in_view(self.SS.Sol):
            self.View.draw_sun(self.SS.Sol)
        for p in self.SS.Sol.satellites:
            if self.View.in_view(p):
                self.View.draw_planet(p)
            # draw orbit
            if self.View.area.overlap(p.orbit.area):
                self.View.draw_orbit(p.orbit)
            for s in p.satellites:
                if self.View.in_view(p):
                    self.View.draw_satellite(s)
                if self.View.area.overlap(s.orbit.area):
                    self.View.draw_orbit(s.orbit)
        for s in self.SS.ships:
            if self.View.in_view(s):
                self.View.draw_ship(s)


    # Handles events
    def event_loop(self):
        events=pg.event.get()
        #for event in events:
        while events:
            event=events.pop(0)
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.KEYDOWN:
                print(events)
                if self.console_active:
                    events.insert(0,event)
                    if self.console.update(events):
                        # pressed enter
                        t=self.console.get_text()
                        self.console.clear_text()
                        self.console.get_surface().fill((0,0,0))
                        print(t)
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
                    if event.key == pg.K_t:
                        self.update_time_rate()
                    if event.key == pg.K_p:
                        if self.time_rate_index!=0:
                            self.time_rate_index=0
                        else:
                            self.time_rate_index = 1
            elif event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                if self.console_area.collidepoint(pos[0],pos[1]):
                    self.console_active=True
                else:
                    self.console_active=False



# En cada tick se actualiza el sistema.
# A 10 FPS el sistema se actualiza 10 veces por segundo, por tanto, el delta es 100ms
# tomamos esto como Time_rate x1, el valor que pasamos al update en segundos es el delta/1000 (0.1s)
# Time_rate x10 el valor al delta es 1s cada tick
# en general el valor para el update es (delta/1000)*Time_rate

    def run(self):
        while not self.done:
            self.event_loop()
            self.clock.tick(FPS)
            # instead of getting the ticks from clock.tick. I assume it works fine and calculate directly
            # mmmmm, doesn't look right
            self.dt = 1000/FPS # milliseconds per frame
            self.dt *= TIME_RATE[self.time_rate_index]
            #print(self.dt)
            if self.time_rate_index!=0:
                self.SS.update(self.dt)
            self.draw()
            pg.display.update()
        pg.quit()
        sys.exit()
