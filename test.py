import sys
from geometry import *
from display import *
from view import *
import pygame as pg
from fspace import *
from geometry import *

global O

done=False

def event_loop():
    global done
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True

def run():
    setup()
    while not done:
        event_loop()
        update()
        draw()
        pg.display.update()
    pg.quit()
    sys.exit()

def setup():
    global area
    #area=Rectangle(-500,750/2,1000,1000*0.75)
    area=Rectangle(-0.5e12,3e11,1e12,0.75*1e12)

    #Display.draw_line_cartesian(Pos(0,area.top),Pos(0,area.bottom),area)
    #Display.draw_line_cartesian(Pos(area.left,0),Pos(area.right,0),area)
    #Display.draw_Xmarks_cartesian(0,area)
    #Display.draw_Ymarks_cartesian(0,area)

    global T
    T=Sun(name="Sol",mass=5.97e24, radius=10)
    T.pos=Pos(0,0)
    global sh
    sh=Ship(T,"noster",10,Pos(1e6,0))
    sh.velocity=Vector(pos=Pos(0,5))
    sh.update_pos(10e-4)

    # Nice elliptical orbit
    #sh=Ship(T,"noster",10,Pos(200,0))
    #sh.velocity=Vector(pos=Pos(0,10))
    #sh.update_pos(10e-4)


    (e,peri, apo, incl) = sh.orbital_params()
    global O
    if e<1:
        O=Orbit(focus1=sh.primary.pos,peri=peri,apo=apo,incl=incl)
    else:
        O=None



def draw():
    Display.screen.fill((0, 0, 0))
    #Display.draw_line_cartesian(Pos(0,area.top),Pos(0,area.bottom),area)
    #Display.draw_line_cartesian(Pos(area.left,0),Pos(area.right,0),area)
    # c=10
    # r=10
    # for f in pg.font.get_fonts():
    #     try:
    #         Display.font=pg.font.SysFont(f, 12)
    #         Display.draw_text(f, Pos(c, r))
    #         r+=15
    #         if r>750:
    #             if c==10:
    #                 c=256
    #             elif c==256:
    #                 c=512
    #             elif c==512:
    #                 c=768
    #             r=10
    #     except:
    #         pass
    #pg.display.update()

    global sh
    global T
    #Display.draw_circle_cartesian(T.pos, 1000, area)
    View.draw_planet(T)
    View.draw_ship(sh)
    #if O:
     #   View.draw_orbit(O)

def update():
    global SIGNX
    global SIGNY
    # sh.velocity+=Pos(SIGNX,SIGNY)
    # if sh.velocity.x==-10:
    #     SIGNX=1
    # if sh.velocity.y==10:
    #     SIGNY=-1
    # elif sh.velocity.y==-10:
    #     SIGNY=1
    sh.update_pos(10e-3)
    pass

    # while x<=earea.right:
    #     y=e._y(x)
    #     if y:
    #         Display.draw_point_cartesian(Pos(x,y[0]),area)
    #         Display.draw_point_cartesian(Pos(x, y[1]), area)
    #     x+=0.5


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





# Sol=Sun(name="sol",mass=1.989E+30,radius=696E+6)
#
# s=Ship(Sol,"noster",1000,Pos(4e6,4e6))
# f=s.Fg()
# print(f)
#
# exit(0)
#
# T=Planet(primary=Sol,name="Earth",mass=5.97E+24, radius=6.38E+6, apo=1.47E+11, peri=1.52E+11,\
#          incl=0,init_pos=0)
#
# v=Vector(Pos(0,5))
# print(v)
# v=Vector(Pos(5,0))
# print(v)
# v=Vector(Pos(0,0))
# print(v)
# v=Vector(Pos(5,5))
# print(v)
# v=Vector(Pos(-5,5))
# print(v)
# v=Vector(Pos(5,-5))
# print(v)
# v=Vector(Pos(-5,-5))
# print(v)
#
# w=Vector(Pos(3,-2))
# print(w)
# v=w*4
# print(v)
# exit(0)

# v=Vector(Pos(5,5))
# print(v)
# v.magnitude=10
# print(v)
# exit(0)

global SIGNX
SIGNX=-1
global SIGNY
SIGNY=1
X=0
Display = Display(1024)

View=View(Display,width=2048)
run()
print("weeey")
exit(0)

