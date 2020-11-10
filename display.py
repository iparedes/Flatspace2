import pygame as pg
from geometry import *
import math

SCREEN_RATIO = 0.75  # 4:3

WHITE = (200, 200, 200)
LIGTH_GRAY = (128,128,128)
CONSOLE_COLOR = (32,32,32,0)
GRAY = (50,50,50)
LINE_WIDTH = 1

ALIGN_LEFT=0
ALIGN_CENTER=1

MARGIN=10

TOPLEFT=0

class Display:
    def __init__(self, width):
        pg.init()
        pg.font.init()

        self.WIDTH = width
        self.HEIGHT = int(width * SCREEN_RATIO)
        pg.display.set_caption("Test")
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font= pg.font.SysFont('arial', 12)
        self.running = True
        self.info_box=[None]*4
        self.info_coordsy=[None]*4
        self.info_coordsy[0]=MARGIN

    # returns true if the coords x,y belong to the display
    def belongs(self,x,y):
        if x<=self.WIDTH and y<=self.HEIGHT:
            return True
        else:
            return False

    # translates cartesian pos from area to display coords
    def trans(self, pos, area):
        xp = int((self.WIDTH / area.width) * (pos.x - area.left))
        yp = int((self.HEIGHT / area.height) * (area.top - pos.y))
        return Pos(xp, yp)

    def test_circle(self):
        # pg.draw.circle(self.main_surface,(255,0,0),(100,100),50)
        pg.draw.ellipse(self.screen, (0, 0, 255), pg.Rect(200, 200, 50, 100))

    def draw_text(self,t,pos,color=WHITE,align=ALIGN_LEFT):
        textsurface = self.font.render(t, False, color)
        if align==ALIGN_CENTER:
            r=textsurface.get_rect()
            deltaP=Pos(-(r.width/2),0)
            pos+=deltaP
        self.screen.blit(textsurface, pos.coords())

    # Draws a point at Pos
    def draw_point(self, Pos):
        self.screen.set_at(Pos.coords(), WHITE)

    def draw_point_cartesian(self,pos,area):
        p=self.trans(pos,area)
        self.draw_point(p)

    def draw_circle_cartesian(self, pos, radius, area):
        p=self.trans(pos,area)
        ratio = area.width / self.WIDTH
        rad=int(radius/ratio)
        self.draw_circle(p,rad)


    def draw_circle(self, pos, radius, linewidth=0):
        pg.draw.circle(self.screen, WHITE, pos.coords(), radius, linewidth)

    def draw_Xmarks_cartesian(self,k,area):
        step=self.WIDTH/area.width
        y=k
        x=area.left
        while x<=area.right:
            p=self.trans(Pos(x,y),area)
            p1=p+Pos(0,-2)
            p2 = p + Pos(0, +2)
            pg.draw.line(self.screen,WHITE,p1.coords(),p2.coords(),LINE_WIDTH)
            x+=1

    def draw_Ymarks_cartesian(self,k,area):
        step=self.WIDTH/area.height
        y=area.top
        x=k
        while y>=area.bottom:
            p=self.trans(Pos(x,y),area)
            p1=p+Pos(-2,0)
            p2 = p + Pos(2,0)
            pg.draw.line(self.screen,WHITE,p1.coords(),p2.coords(),LINE_WIDTH)
            y-=1

    def draw_line(self,p1,p2):
        pg.draw.line(self.screen,WHITE,p1.coords(),p2.coords(),LINE_WIDTH)

    def draw_line_cartesian(self,pos1,pos2,area):
        p1=self.trans(pos1,area)
        p2 = self.trans(pos2, area)
        pg.draw.line(self.screen,WHITE,p1.coords(),p2.coords(),LINE_WIDTH)

    def draw_rectangle_cartesian(self, rect, area):
        ratio = area.width / self.WIDTH
        pos = self.trans(Pos(rect.left, rect.top), area)
        w = rect.width / ratio
        h = rect.height / ratio
        new_r = pg.Rect(pos.x, pos.y, w, h)
        self.draw_rectangle(new_r)


    def draw_rectangle(self, topleft,width,height,color=WHITE):
        r=pg.Rect(topleft,(width,height))
        pg.draw.rect(self.screen, color, r, LINE_WIDTH)


    def draw_ellipse_cartesian(self, ellipse, area):
        ratio = area.width / self.WIDTH
        a = ellipse.a / ratio
        b = ellipse.b / ratio
        pos = self.trans(ellipse.center, area)
        self.draw_ellipse(pos, a, b, ellipse.incl)


        # BREAKS WITH WIDTH OR HEIGHT TOO LARGE, LOOKS LIKE THE VALUES THAT I AM PASSING HERE ARE UNIVERSE VALUES,
        # AND SHOULD BE DISPLAY VALUES
        # Pos is the center, a, b are semi-major and semi-minor axis
        # rot is the rotation in degrees, counterclockwise


    def draw_ellipse(self, pos=None, a=0, b=0, rot=0, ellipse=None):
        if ellipse:
            a = ellipse.a
            b = ellipse.b
            r=ellipse.c
            pos = ellipse.center
            rot = ellipse.incl
        else:
            r = math.sqrt((a ** 2) - (b ** 2))

        w = a * 2
        h = b * 2
        # print("w:"+str(w))
        # print("h:"+str(h))
        surface = pg.Surface((w, h), pg.SRCALPHA, 32)
        surface = surface.convert_alpha()
        size = (0, 0, w, h)
        ellipse = pg.draw.ellipse(surface, WHITE, size, LINE_WIDTH)
        corner_pos = Pos(pos.x - a, pos.y - b)
        # self.screen.blit(surface,corner_pos.coords())

        orig_center = ellipse.center

        # Creates a new rotated surface. Beware that it is not really a rotated suface, but a bigger new one that
        # has the rotated original surface inside
        surface2 = pg.transform.rotate(surface, rot)

        # moves the rotated surface to match the center of the original one
        rot_rect = surface2.get_rect()
        new_center = rot_rect.center
        deltax = orig_center[0] - new_center[0]
        deltay = orig_center[1] - new_center[1]

        corner_pos += Pos(deltax, deltay)
        self.screen.blit(surface2, corner_pos.coords())

        # Ojo a partir de aqui
        # # so at this point, we have the original ellipse rotated from the center
        # # but we need it rotated from the focus, so we need to move it again
        #
        # # moves to match the focus
        # # calculates the new position of the focus
        # orig_focus=Pos(-r,0)
        # # **
        # #newx = -r * math.cos(math.radians(rot))
        # #newy = -r * math.sin(math.radians(rot))
        # newx = r * math.cos(math.radians(rot))
        # newy = r * math.sin(math.radians(rot))
        # # calculates the delta between the old and new focus
        # #
        # deltax = (orig_focus.x - newx)
        # deltay=(newy-orig_focus.y)
        # pos += Pos(deltax, deltay)
        #
        # corner_pos+=pos


    def draw_path(self,path,color=GRAY):
        p1=path.pop()
        while path:
            p2=path.pop()
            if self.belongs(p1.x,p1.y) or self.belongs(p2.x,p2.y):
                pg.draw.line(self.screen, color, p1.coords(), p2.coords(), LINE_WIDTH)
            p1=p2

    def draw_ex(self,pos):
        p1 = pos + Pos(0, -2)
        p2 = pos + Pos(0, +2)
        pg.draw.line(self.screen, WHITE, p1.coords(), p2.coords(), LINE_WIDTH)
        p1 = pos + Pos(-2,0)
        p2 = pos + Pos(2, 0)
        pg.draw.line(self.screen, WHITE, p1.coords(), p2.coords(), LINE_WIDTH)


    def draw_info(self,info,pos=0):
        text=info()
        t=text.split('\n')
        width=0
        height=0

        if self.info_box[pos]==None:
            return
        if pos>=len(self.info_coordsy):
            pos=0
        if pos==0:
            coords=[MARGIN,MARGIN]
            topleft=(MARGIN,MARGIN) # This is used later to draw the background square
        else:
            y=self.info_coordsy[pos-1]+MARGIN
            coords = [MARGIN,y]
            topleft = (MARGIN,y)
        if coords:
            surfaces=[]
            for l in t:
                textsurface = self.font.render(l, False, WHITE)
                r = textsurface.get_rect()
                if r.width>width:
                    width=r.width
                height+=r.height
                elem=(textsurface,tuple(coords))
                surfaces.append(elem)
                coords[1]+=r.height
            r = pg.Rect(topleft, (width, height))
            self.info_coordsy[pos]=r.bottom
            pg.draw.rect(self.screen, CONSOLE_COLOR, r, 0)
            for e in surfaces:
                self.screen.blit(e[0], e[1])

    def draw_info_boxes(self):
        for i in range(0,len(self.info_box)):
            if self.info_box[i]:
                self.draw_info(self.info_box[i],i)






