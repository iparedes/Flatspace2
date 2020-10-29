from geometry import *

PATH_RESOLUTION=100
EPSILON=10E-9 # small number used to avoid non existing values in the ellipse when calculating in the border of its area

# Defines an area in the flatspace with cartesian coordinates
class View:

    # w: width in meters of the view
    # pos: center point of the view rectangle
    def __init__(self, display, width=0,pos=Pos(0, 0)):
        height = int(width * 0.75)
        self.area = Rectangle(int(pos.x - width / 2), int(pos.y + height / 2), width, height)

        self.display = display
        self.mperpixel = (self.area.width / self.display.WIDTH)

    def set_center(self, pos):
        self.area.center = pos

    # moves the display (x,y) units
    def move(self, x, y):
        if y == 0:
            vert_step = 0
        else:
            vert_step = self.area.height / y
        if x == 0:
            hori_step = 0
        else:
            hori_step = self.area.width / x
        p = Pos(self.area.center.x + hori_step, self.area.center.y + vert_step)
        self.area.center = p

    # factor: percentage of zoom increase (positive level) or decrease (negative level) of the current vi
    def zoom(self, level):
        factor = (100 - level) / 100
        self.area.width *= factor
        self.area.height *= factor
        self.mperpixel = self.area.width / self.display.WIDTH
        print("Width: "+str(self.area.width)+", mpp: "+str(self.mperpixel))


    def in_view(self, element):
        a=element.area
        if self.area.contains(a):
            return True
        else:
            return self.area.intersects(a)

    # translates a position from the view (cartesian origin) to the display (top left corner origin)
    def trans(self, pos):
        xp = int((self.display.WIDTH/self.area.width)*(pos.x-self.area.left))
        yp = int((self.display.HEIGHT/self.area.height)*(self.area.top-pos.y))
        return Pos(xp, yp)

    def draw_planet(self,planet):
        pos=self.trans(planet.pos)
        radius=int(planet.radius/self.mperpixel)
        if radius==0:
            radius=1
        self.display.draw_circle(pos, radius)

    def draw_sun(self,sun):
        pos=self.trans(sun.pos)
        radius=int(sun.radius/self.mperpixel)
        if radius==0:
            radius=1
        self.display.draw_circle(pos, radius)


    def draw_orbit(self,orbit):
        ellipse=orbit.ellipse

        self.display.draw_ex(self.trans(ellipse.focus1))


        # OjO
        #self.display.draw_ellipse_cartesian(ellipse,self.area)

        ellipse_area=ellipse.area
        rect=self.area

        ips=ellipse.intersect_points_with_rect(rect)
        xpoints=ips['x']
        ypoints = ips['y']
        nx=len(xpoints)
        ny=len(ypoints)
        print(nx,ny)
        x1=0
        x2=0
        if nx==0:
            if ny==0:
                # ellipse totally contained
                x1=ellipse_area.left
                x2=ellipse_area.right
                # center = ellipse.center
                # pos = self.trans(center)
                # a = int(ellipse.a / self.mperpixel)
                # b = int(ellipse.b / self.mperpixel)
                # self.display.draw_ellipse(pos, a, b, orbit.incl)
                # return
                #self.display.draw_ellipse_cartesian(ellipse,rect)
            else:
                x1 = ypoints[0].x
                x2 = ypoints[1].x
                l = [x1, x2]
                if rect.left < ellipse_area.left < rect.right:
                    l.append(ellipse.area.left + EPSILON)
                if rect.left < ellipse_area.right < rect.right:
                    l.append(ellipse.area.right - EPSILON)
                l.sort()
                print(l)
                x1 = l[0]
                x2 = l[len(l) - 1]
        elif nx==1:
            if ny==1:
                # corner cut
                x1=xpoints[0].x
                x2=ypoints[0].x
                l=[x1,x2]
                if rect.left < ellipse_area.left < rect.right:
                    l.append(ellipse.area.left+EPSILON)
                if rect.left < ellipse_area.right < rect.right:
                    l.append(ellipse.area.right-EPSILON)
                l.sort()
                x1=l[0]
                x2=l[-1]
            else: #ny==3
                # corner cut + vertical bridge
                x1=xpoints[0].x
                x2=ypoints[0].x
                l=[x1,x2]
                if rect.left < ellipse_area.left < rect.right:
                    l.append(ellipse.area.left+EPSILON)
                if rect.left < ellipse_area.right < rect.right:
                    l.append(ellipse.area.right-EPSILON)
                l.sort()
                x1=l[0]
                x2=l[-1]
        elif nx==2:
            if ny==0: # crossing vertical edge
                if xpoints[0].x==xpoints[1].x:
                    # lobe cutting one edge
                    x1=xpoints[0].x
                    if rect.left<ellipse_area.left<rect.right:
                        x2 = ellipse_area.left+EPSILON
                    else:
                        x2 = ellipse_area.right-EPSILON
                else:
                    # cutting both edges across
                    x1=xpoints[0].x
                    x2=xpoints[1].x
                    pass
            elif ny==2: # ny==2
                # Two corner cuts
                l=[p.x for p in xpoints+ypoints]
                if rect.left < ellipse_area.left < rect.right:
                    l.append(ellipse.area.left+EPSILON)
                if rect.left < ellipse_area.right < rect.right:
                    l.append(ellipse.area.right-EPSILON)
                l.sort()
                x1=l[0]
                x2=l[-1]
                # x1=xpoints[0].x
                # x2=ypoints[0].x
                # l=[x1,x2]
                # if rect.left < ellipse_area.left < rect.right:
                #     l.append(ellipse.area.left+EPSILON)
                # if rect.left < ellipse_area.right < rect.right:
                #     l.append(ellipse.area.right-EPSILON)
                # l.sort()
                # x1=l[0]
                # x2=l[-1]
            else: # ny==4
                l=[p.x for p in xpoints]
                if rect.left < ellipse_area.left < rect.right:
                    l.append(ellipse.area.left+EPSILON)
                if rect.left < ellipse_area.right < rect.right:
                    l.append(ellipse.area.right-EPSILON)
                l.sort()
                x1=l[0]
                x2=l[-1]
        elif nx==3:
            # corner cut + horizontal bridge
            if ny==1:
                x1=xpoints[0].x
                x2=ypoints[0].x
                l=[p.x for p in xpoints+ypoints]
                #l=[x1,x2]
                if rect.left < ellipse_area.left < rect.right:
                    l.append(ellipse.area.left+EPSILON)
                if rect.left < ellipse_area.right < rect.right:
                    l.append(ellipse.area.right-EPSILON)
                l.sort()
                x1=l[0]
                x2=l[-1]
            else: # ny==3
                x1=rect.left
                x2=rect.right

        else: # nx==4
            l = [rect.left,rect.right]
            if rect.left < ellipse_area.left < rect.right:
                l.append(ellipse.area.left + EPSILON)
            if rect.left < ellipse_area.right < rect.right:
                l.append(ellipse.area.right - EPSILON)
            l.sort()
            x1 = l[0]
            x2 = l[len(l) - 1]

        paths = ellipse.paths(x1, x2, PATH_RESOLUTION)
        path = paths[0]
        path_conv = [self.trans(p) for p in path]
        self.display.draw_path(path_conv)
        path = paths[1]
        path_conv = [self.trans(p) for p in path]
        self.display.draw_path(path_conv)

    # def draw_orbit(self,orbit):
    #     ellipse=orbit.ellipse
    #
    #     self.display.draw_ex(self.trans(ellipse.focus1))
    #
    #
    #     # OjO
    #     #self.display.draw_ellipse_cartesian(ellipse,self.area)
    #
    #     ellipse_area=ellipse.area
    #     rect=self.area
    #
    #     ips=ellipse.intersect_points_with_rect(rect)
    #     xpoints=ips['x']
    #     ypoints = ips['y']
    #     nx=len(xpoints)
    #     ny=len(ypoints)
    #     print(nx,ny)
    #     if nx==0:
    #         if ny==0:
    #             # ellipse totally contained
    #             center = ellipse.center
    #             pos = self.trans(center)
    #             a = int(ellipse.a / self.mperpixel)
    #             b = int(ellipse.b / self.mperpixel)
    #             self.display.draw_ellipse(pos, a, b, orbit.incl)
    #             #self.display.draw_ellipse_cartesian(ellipse,rect)
    #         elif ny==2: # vertical lobe, or vertical bridge
    #             if ypoints[0].y==ypoints[1].y:
    #                 # Lobe cutting a horizontal edge (vertical lobe)
    #                 x1=ypoints[0].x
    #                 x2=ypoints[1].x
    #                 if (x1>x2):
    #                     (x1,x2)=(x2,x1)
    #                 if x1>ellipse_area.left:
    #                     x1=ellipse_area.left
    #                 if x2<ellipse_area.right:
    #                     x2=ellipse_area.right
    #                 paths=ellipse.paths(x1,x2,PATH_RESOLUTION)
    #                 path = paths[0]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #                 path = paths[1]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #             else: # vertical bridge
    #                 x1=ypoints[0].x
    #                 x2=ypoints[1].x
    #                 if rect.left<ellipse_area.left<rect.right:
    #                     # left point limit inside view
    #                     l=[x1,x2,ellipse_area.left]
    #                     l.sort()
    #                     x1=l[0]
    #                     x2=l[2]
    #                 elif rect.left<ellipse_area.right<rect.right:
    #                     # right point limit inside view
    #                     l=[x1,x2,ellipse_area.right]
    #                     l.sort()
    #                     x1=l[0]
    #                     x2=l[2]
    #                 else: # just a simple bridge
    #                     # no need to do anything
    #                     pass
    #                 paths = ellipse.paths(x1, x2, PATH_RESOLUTION)
    #                 path = paths[0]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #                 path = paths[1]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #         else: # ny==4, two vertical bridges
    #             x1 = ypoints[0].x
    #             x2 = ypoints[1].x
    #             l=[x1,x2]
    #             if rect.left < ellipse_area.left < rect.right:
    #                 l.append(ellipse.area.left)
    #             if rect.left < ellipse_area.right < rect.right:
    #                 l.append(ellipse.area.right)
    #             l.sort()
    #             x1=l[0]
    #             x2=l[3]
    #             paths = ellipse.paths(x1, x2, PATH_RESOLUTION)
    #             path = paths[0]
    #             path_conv = [self.trans(p) for p in path]
    #             self.display.draw_path(path_conv)
    #             path = paths[1]
    #             path_conv = [self.trans(p) for p in path]
    #             self.display.draw_path(path_conv)
    #     elif nx==1:
    #         if ny==1:
    #             # corner cut
    #             x1=xpoints[0].x
    #             x2=ypoints[0].x
    #             l=[x1,x2]
    #             if rect.left < ellipse_area.left < rect.right:
    #                 l.append(ellipse.area.left)
    #             if rect.left < ellipse_area.right < rect.right:
    #                 l.append(ellipse.area.right)
    #             l.sort()
    #             x1=l[0]
    #             x2=l[len(l)-1]
    #             paths = ellipse.paths(x1, x2, PATH_RESOLUTION)
    #             path = paths[0]
    #             path_conv = [self.trans(p) for p in path]
    #             self.display.draw_path(path_conv)
    #             path = paths[1]
    #             path_conv = [self.trans(p) for p in path]
    #             self.display.draw_path(path_conv)
    #         else: #ny==3
    #             # corner cut + vertical bridge
    #             pass
    #     elif nx==2:
    #         if ny==0: # crossing vertical edge
    #             if xpoints[0].x==xpoints[1].x:
    #                 # lobe cutting one edge
    #                 x1=xpoints[0].x
    #                 if rect.left<ellipse_area.left<rect.right:
    #                     x2 = ellipse_area.left
    #                 else:
    #                     x2 = ellipse_area.right
    #                 paths=ellipse.paths(x1,x2,PATH_RESOLUTION)
    #                 path = paths[0]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #                 path = paths[1]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #             else:
    #                 # cutting both edges across
    #                 x1=xpoints[0].x
    #                 x2=xpoints[1].x
    #                 paths=ellipse.paths(x1,x2,PATH_RESOLUTION)
    #                 path = paths[0]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #                 path = paths[1]
    #                 path_conv = [self.trans(p) for p in path]
    #                 self.display.draw_path(path_conv)
    #
    #                 pass
    #         else: # ny==2
    #             # Two corner cuts
    #             x1=xpoints[0].x
    #             x2=ypoints[0].x
    #             l=[x1,x2]
    #             if rect.left < ellipse_area.left < rect.right:
    #                 l.append(ellipse.area.left)
    #             if rect.left < ellipse_area.right < rect.right:
    #                 l.append(ellipse.area.right)
    #             l.sort()
    #             x1=l[0]
    #             x2=l[len(l)-1]
    #             paths = ellipse.paths(x1, x2, PATH_RESOLUTION)
    #             path = paths[0]
    #             path_conv = [self.trans(p) for p in path]
    #             self.display.draw_path(path_conv)
    #             path = paths[1]
    #             path_conv = [self.trans(p) for p in path]
    #             self.display.draw_path(path_conv)
    #     elif nx==3:
    #         pass
    #     else: # nx==4
    #         pass