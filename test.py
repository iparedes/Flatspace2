from geometry import *
from display import *
import pygame as pg
#from fspace import *

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
    print(earea)
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


    pass

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


# e=Ellipse(100,40,Pos(0,0))
# print(e)
# e.incl=30
# print(e)
#exit(0)

Display = Display(1024)
run()
print("weeey")
exit(0)

class A:
    def __init__(self):
        self._a=0

    @property
    def a(self):
        return self._a

class B(A):
    def __init__(self):
        pass

    @A.a.setter
    def a(self,v):
        self._a=v

test=B()
B.a=99
print(B.a)

exit(0)


p=Pos(0,0)
e=Ellipse(center=p,a=20,b=20,incl=0)
print(e)
q=Pos(20,20)
e.center=q
print(e)
f=Pos(-6.770509831248425,-9.68245836551854)
e.focus1=f
print(e)
e.a=100
print(e)

exit(0)

Sol=Body()
Sol.mass = 1e6
Sol.radius = 10000
Sol.pos = Pos(0, 0)

P=Body()
P.mass=1e4
P.radius=1000
o=Orbit(10,10,30)
P.set_orbit(o,Sol)
# print(o)
#
# t=o.intersects_X(5)
# print(t)
# t=o.intersects_Y(-5)
# print(t)

a=Rectangle(0,0,200,100)
b=Rectangle(-10,-10,1000,1000)
print(a)
print(b)
print(a.intersects_X(b))
print(b.intersects_X(a))


# R=Rectangle(-20,200,100,200)
# t=R.overlap(o.area())
# print(t)