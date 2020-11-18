from geometry import *
from display import *

PATH_RESOLUTION=100
EPSILON=10E-1 # small number used to avoid non existing values in the ellipse when calculating in the border of its area
DEFAULT_PLANET_RADIUS=5 # radius to draw when the planet is too small to be seen
DEFAULT_SUN_RADIUS=10 # radius to draw when the planet is too small to be seen
DEFAULT_SHIP_SIZE=10
LABEL_MARGIN=5

# Defines an area in the flatspace with cartesian coordinates
class View:

    # w: width in meters of the view
    # pos: center point of the view rectangle
    def __init__(self, display, width=0,pos=Pos(0, 0)):
        height = int(width * 0.75)
        self.area = Rectangle(int(pos.x - width / 2), int(pos.y + height / 2), width, height)

        self.display = display
        self.mperpixel = (self.area.width / self.display.WIDTH)

        self.labels=True

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

    # level: percentage of zoom increase (+) or decrease (-)
    # a level of 10 means that the factor to calculate the new area will be 90%
    # a level of -10 means that the factor to calculate the new area will be 110%
    def zoom(self, level):
        factor = (100 - level) / 100
        self.area.width *= factor
        self.area.height *= factor
        self.mperpixel = self.area.width / self.display.WIDTH
        #print("Width: "+str(self.area.width)+", mpp: "+str(self.mperpixel))

    def in_view(self, element=None):
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

    def draw_ship(self,s):
        # Creates the body of the ship
        r = Rectangle(0, 0, 100, 100)
        # Moves the body to match the position of the ship
        r.center = s.pos
        # Translates the coordinates of the body
        # uses both corners to determine the width and height translated
        topleft=self.trans(Pos(r.left,r.top))
        bottomright=self.trans(Pos(r.right,r.bottom))
        w=bottomright.x-topleft.x
        h=bottomright.y-topleft.y
        # Draws the body of the ship in the Display
        if w<50:
            centerx=topleft.x+(w/2)
            centery=topleft.y+(h/2)
            newx=centerx-(DEFAULT_SHIP_SIZE/2)
            newy=centery-(DEFAULT_SHIP_SIZE/2)
            self.display.draw_rectangle((newx,newy),DEFAULT_SHIP_SIZE,DEFAULT_SHIP_SIZE)
        else:
            self.display.draw_rectangle(topleft.coords(),w,h)
        # Draws the velocity vector
        alfa=s.velocity.direction_radians
        x2=20*math.cos(alfa)
        y2=20*math.sin(alfa)
        pos1=self.trans(s.pos)
        pos2=pos1+Pos(x2,-y2)
        #pos2=s.pos+Pos(x2,y2)
        #pos2=self.trans(pos2)
        self.display.draw_line(pos1,pos2)

        # Projection
        self.display.draw_path(s.path)

        self.display.draw_text(s.primary.name,bottomright)


    def draw_planet(self,planet):
        pos=self.trans(planet.pos)
        radius=int(planet.radius/self.mperpixel)
        if radius==0:
            radius=DEFAULT_PLANET_RADIUS
        self.display.draw_circle(pos, radius)
        if self.labels:
            pos+=Pos(0,10)
            self.display.draw_text(planet.name,pos,color=LIGTH_GRAY,align=ALIGN_CENTER)



    def draw_satellite(self,planet):
        pos=self.trans(planet.pos)
        radius=int(planet.radius/self.mperpixel)
        if radius==0:
            radius=DEFAULT_PLANET_RADIUS
        self.display.draw_circle(pos, radius)
        if self.labels:
            pos+=Pos(0,10)
            self.display.draw_text(planet.name,pos,color=LIGTH_GRAY,align=ALIGN_CENTER)



    def draw_sun(self,sun):
        pos=self.trans(sun.pos)
        radius=int(sun.radius/self.mperpixel)
        if radius==0:
            radius=DEFAULT_SUN_RADIUS
        self.display.draw_circle(pos, radius,1)
        if self.labels:
            pos+=Pos(0,10)
            self.display.draw_text(sun.name,pos,color=LIGTH_GRAY,align=ALIGN_CENTER)


    def draw_orbit(self,orbit):
        ellipse=orbit.ellipse

        self.display.draw_ex(self.trans(ellipse.focus1))

        ellipse_area=ellipse.area
        rect=self.area

        ips=ellipse.intersect_points_with_rect(rect)
        xpoints=ips['x']
        ypoints = ips['y']
        nx=len(xpoints)
        ny=len(ypoints)
        #print(nx,ny)
        x1=0
        x2=0
        try:
            if nx==0:
                if ny==0:
                    # ellipse totally contained
                    x1=ellipse_area.left+EPSILON
                    x2=ellipse_area.right-EPSILON
                elif ny==1:
                    # dont know why we get here
                    print(ypoints[0])
                    pass
                else:
                    x1 = ypoints[0].x
                    x2 = ypoints[1].x
                    l = [x1, x2]
                    if rect.left < ellipse_area.left < rect.right:
                        l.append(ellipse.area.left + EPSILON)
                    if rect.left < ellipse_area.right < rect.right:
                        l.append(ellipse.area.right - EPSILON)
                    l.sort()
                    x1 = l[0]
                    x2 = l[-1]
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
                    l=[p.x for p in xpoints+ypoints]
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
                x2 = l[-1]
        except:
            print("xpoints: ",end='')
            for p in xpoints:
                print(p,end=',')
            print("ypoints: ",end='')
            for p in ypoints:
                print(p,end=',')
            exit(-1)

        paths = ellipse.paths(x1, x2, PATH_RESOLUTION)
        path = paths[0]
        path_conv = [self.trans(p) for p in path]

        label_done=False
        if self.labels:
            pos=path_conv[int(len(path_conv)/2)]
            if self.display.belongs(pos.x,pos.y):
                self.display.draw_text(orbit.name,pos,color=LIGTH_GRAY,align=ALIGN_CENTER)
                label_done=True
        self.display.draw_path(path_conv)

        path = paths[1]
        path_conv = [self.trans(p) for p in path]
        if self.labels and not label_done:
            pos=path_conv[int(len(path_conv)/2)]
            self.display.draw_text(orbit.name,pos,color=LIGTH_GRAY,align=ALIGN_CENTER)
        self.display.draw_path(path_conv)

