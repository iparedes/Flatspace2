import sys
from view import *
from display import *
from geometry import *
from fspace import *
import pygame as pg
import cProfile

ZOOM_FACTOR = 10
MOVE_FACTOR = 10

class Game(object):
    def __init__(self):
        self.done = False
        self.SS=SSystem()

        self.max_apo=0
        self.max_peri=0 # watchout that max_peri is not the biggets periapsis, but the pri corresponding to max_apo
        self.load_data()
        self.clock = pg.time.Clock()
        self.Display = Display(1024)
        # sets the view with the sun in the center to accommodate to see complete the largest orbit
        # it is not totally correct as it assumes that the orbit is horizontal in the ref. coords
        self.View=View(self.Display,width=(self.max_apo*2.05))
        #self.View = View(self.Display, width=800)
        center=Pos(0,0)
        pos_display=self.View.trans(center)
        self.Display.draw_point(pos_display)

        # This is only for testing purposes. The parent of the orbit should be the Sun, not the planet
        # P=Planet("test",1e9,6e6,Pos(5e6,5e6))
        # O=Orbit(0.47E+11, 9.52E+11,30)
        # O.body=P
        # self.View.draw_planet(P)
        # self.View.draw_orbit(O)

    def load_data(self):
        file1 = open('data', 'r')
        Lines = file1.readlines()
        for l in Lines:
            l.strip()
            if l[0] != '#':
                l.rstrip()
                items = l.split(',')
                if items[0] == "Sun":
                    self.SS.Sol.mass = float(items[1])
                    self.SS.Sol.radius = float(items[2])
                    self.SS.Sol.pos = Pos(0, 0)
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
                    self.SS.Sol.add_planet(P)


    def draw(self):
        self.Display.screen.fill((0, 0, 0))
        if self.View.in_view(self.SS.Sol):
            self.View.draw_sun(self.SS.Sol)
        for p in self.SS.Sol.satellites:
            if self.View.in_view(p):
                self.View.draw_planet(p)
            # draw orbit
            #print(self.View.area)
            #print(p.orbit.area)
            if self.View.area.overlap(p.orbit.area):
                pr = cProfile.Profile()
                pr.enable()
                self.View.draw_orbit(p.orbit)
                pr.disable()
                # after your program ends
                pr.print_stats(sort="calls")
            else:
                print("No orbit")




    # Handles events
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.KEYDOWN:
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



    def run(self):
        while not self.done:
            self.clock.tick(10)
            self.event_loop()
            self.draw()
            pg.display.update()
        pg.quit()
        sys.exit()
