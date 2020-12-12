from fspace import *
from copy import copy, deepcopy
from geometry import *
from display import *
from view import *
import pygame as pg
import sys
import time

done=False

def event_loop():
    global done
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True



Display = Display(1024)
View=View(Display,width=2048)
area=View.area
#Display.draw_Xmarks_cartesian(0,area)
#Display.draw_Ymarks_cartesian(0,area)

#eli=Ellipse(400,0.9,focus1=Pos(0,0),incl=30)
hyp=Hyperbola(200,3.01,focus1=Pos(0,0))
hyp.center=Pos(100,100)
hyp.incl=30
(p1,p2)=hyp.paths(area.left,area.right,200)
p1c = [View.trans(p) for p in p1]
p2c = [View.trans(p) for p in p2]
Display.draw_path(p1c)
Display.draw_path(p2c)

line1=hyp.asymptote1()
line2=hyp.asymptote2()


def update(cont):
    if cont==1:
        eli.a=50
        return
    if cont==2:
        eli.b=100
        return
    if cont==-1:
        eli.focus2=Pos(0,0)
        return


cont=0

while not done:
    #Display.screen.fill((0, 0, 0))
    event_loop()
    #Display.draw_segment_cartesian(Pos(0, area.top), Pos(0, area.bottom), area)
    #Display.draw_segment_cartesian(Pos(area.left, 0), Pos(area.right, 0), area)

    Display.draw_line_cartesian(line1, area)
    Display.draw_line_cartesian(line2, area)

    #Display.draw_ellipse_cartesian(eli,area)
    pg.display.update()
    #update(cont)
    #time.sleep(1)
    #cont+=1
pg.quit()
sys.exit()

