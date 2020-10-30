from geometry import *
from display import *
import pygame as pg
from fspace import *

done=False

def event_loop():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True

def run():
    while not done:
        event_loop()
        draw()
        pg.display.update()
    pg.quit()
    sys.exit()

def draw():
    Display.screen.fill((0, 0, 0))
    area=Rectangle(-50,40,100,100*0.75)

    Display.draw_line_cartesian(Pos(0,area.top),Pos(0,area.bottom),area)
    Display.draw_line_cartesian(Pos(area.left,0),Pos(area.right,0),area)
    Display.draw_Xmarks_cartesian(0,area)
    Display.draw_Ymarks_cartesian(0,area)

    e=Ellipse(a=4,b=2,center=Pos(0,0),incl=30)
    earea=e.area
    x=earea.left

    while x<=earea.right:
        y=e._y(x)
        if y:
            Display.draw_point_cartesian(Pos(x,y[0]),area)
            Display.draw_point_cartesian(Pos(x, y[1]), area)
        x+=0.5


    #e.focus1=Pos(10,10)
    #Display.draw_ex(Display.trans(e.focus1,area))

    #Display.draw_ellipse_cartesian(e,area)
    #r=Rectangle(-12,12,12,12)
    #Display.draw_ellipse_cartesian(e,area)
    #Display.draw_rectangle_cartesian(r,area)

    # points=e.intersect_points_with_rect(r)
    # p1=points['x'][0].x
    # p2 = points['y'][0].x

    #exit(0)

    # paths=e.paths(p1,p2,5)
    # path=paths[1]
    # path_conv=[Display.trans(p,area) for p in path]
    # Display.draw_path(path_conv)
    #path=paths[1]
    #path_conv=[Display.trans(p,area) for p in path]
    #Display.draw_path(path_conv)

    # ps=e.intersect_points_with_rect(r)
    # print("x")
    # for p in ps['x']:
    #     print(p)
    # print("y")
    # for p in ps['y']:
    #     print(p)
    # p=e.intersect_points_X(r.left)
    # print("Intersect left")
    # for a in p:
    #     print(a)
    # p=e.intersect_points_X(r.right)
    # print("Intersect right")
    # for a in p:
    #     print(a)
    # p=e.intersect_points_Y(r.top)
    # print("Intersect top")
    # for a in p:
    #     print(a)
    # p=e.intersect_points_Y(r.bottom)
    # print("Intersect bottom")
    # for a in p:
    #     print(a)


#
Sol=Sun(name="sol",mass=1.989E+30,radius=696E+6)
T=Planet(primary=Sol,name="Earth",mass=5.97E+24, radius=6.38E+6, apo=1.47E+11, peri=1.52E+11,\
         incl=0,init_pos=0)
print(T)
print(T.T/3600/24)
print(T.time/3600/24)
(pos,time)=T.pos_at_angle(180)
print(T.T/3600/24)
print(time/3600/24)

exit(0)


Display = Display(1024)
run()
print("weeey")
exit(0)

