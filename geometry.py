import math

class Pos:

    def __init__(self,x,y):
        self.x=x
        self.y=y

    def __str__(self):
        t="("+str(self.x)+","+str(self.y)+")"
        return t

    def __add__(self, other):
        return Pos(self.x+other.x,self.y+other.y)

    def __sub__(self, other):
        return Pos(self.x-other.x,self.y-other.y)

    def coords(self):
        return (self.x,self.y)

    def distance(self,other):
        return math.sqrt(((self.x-other.x)**2)+((self.y-other.y)**2))


# the reference frame for the rectangle is Cartesian
class Rectangle:

    def __init__(self,left,top,width,height):
        self._top=top
        self._left=left
        self._width=width
        self._height=height
        self._center=Pos(int(left+(width/2)),int(top-(height/2)))
        self._bottom=self._top-self._height
        self._right=self._left+self._width

    def __str__(self):
        t="left:"+str(self.left)+", top:"+str(self.top)+" -> right:"+str(self.right)+", bottom:"+str(self.bottom)
        return t

    # returns true if the point belongs to the rectangle
    def belongs(self,point):
        return self.left<=point.x<=self.right and self.bottom<=point.y<=self.top

    # returns true if there is overlap between self and other
    # overlap can be that one contains the other or an intersection
    def overlap(self,other):
        res= self.left > other.right or self.right < other.left or \
            self.top<other.bottom or self.bottom > other.top
        return not res

    # returns True if self contains other, but not the other way around
    def contains(self,other):
        res = self.left < other.left and self.right>other.right and \
            self.top>other.top and self.bottom<other.bottom
        return res

    # returns True if other intersects any of the vertical sides of self
    def intersects_X(self,other):
        # first checks if other is horizontally aligned with self (are at a similar height)
        res=False
        if (self.bottom<other.top<self.top) or (self.bottom<other.bottom<self.top):
            # now checks if there is intersection on the vertical sides
            res=(other.left<self.left<other.right) or (other.left<self.right<other.right)
        return res

    def intersects_Y(self,other):
        # first checks if other is verticall aligned with self (are at a similar horizontal position)
        res=False
        if (self.left<other.left<self.right) or (self.left<other.right<self.right):
            # now checks if there is intersection on the vertical sides
            res=(other.bottom<self.top<other.top) or (other.bottom<self.bottom<other.top)
        return res

    def intersects(self,other):
        return self.intersects_X(other) or self.intersects_Y(other)

    @property
    def center(self):
        return self._center
    @center.setter
    # p: tupla (x,y)
    def center(self,p):
        x=p.x
        y=p.y
        self._center=p
        self._left=int(x-(self.width/2))
        self._top = int(y + (self.height / 2))
        self._right = self._left + self._width
        self._bottom = self._top - self._height

    @property
    def left(self):
        return self._left
    @left.setter
    def left(self,v):
        self._left=v
        xc=v+int(self.width/2)
        self._right=v+self.width
        self._center.x=xc

    @property
    def right(self):
        return self._right
    @right.setter
    def right(self,v):
        self._right=v
        xc=v-int(self.width/2)
        self._left=v-self.width
        self._center.x=xc


    @property
    def top(self):
        return self._top
    @top.setter
    def top(self, v):
        self._top = v
        yc = v - int(self._height / 2)
        self._center.y = yc
        self._bottom=v-self._height

    @property
    def bottom(self):
        return self._bottom
    @bottom.setter
    def bottom(self,v):
        self._bottom=v
        yc=v+int(self._height/2)
        self._center.y=yc
        self._top=v+self._height

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, v):
        self._width = v
        self._left = self._center.x - int(v / 2)
        self._right=self._left + self._width


    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, v):
        self._height = v
        self._top=self._center.y + int(v / 2)
        self._bottom=self._top-self._height

class Ellipse:
    # a:semi-major axis
    # b:semi-minor axis
    # c: distance from center to focii
    # center: Pos, center of the ellipse
    # focus1: Pos of the left focus (the one to the left of the center when incl=0)
    # focus2: Pos of the right focus (the one to the right of the center when incl=0)
    # incl: in degrees, counterclockwise from the X axis
    def __init__(self,a,b,center=None, focus1=None, focus2=None, incl=0):
        if (a<b):
            (a,b)=(b,a)

        self._incl=incl
        self._a=a
        self._b=b
        self.c = math.sqrt((a ** 2) - (b ** 2))

        if center != None:
            self.center=center
        if focus1 != None:
            self.focus1=focus1
        if focus2 != None:
            self.focus2=focus2
        # c: distance from center to focus
        self._accelerate_calcs()

    def _accelerate_calcs(self):
        self.a2 = self.a ** 2
        self.b2 = self.b ** 2
        self.sin = math.sin(math.radians(self.incl))
        self.cos = math.cos(math.radians(self.incl))
        self.sin2 = self.sin ** 2
        self.cos2 = self.cos ** 2

    def __str__(self):
        t="a: "+str(self._a)+", b: "+str(self._b)+", c: "+str(self.c)+"\n"
        t+="center: "+str(self._center)+", f1: "+str(self._focus1)+"f2: "+str(self._focus2)
        return t

    @property
    def a(self):
        return self._a
    @a.setter
    def a(self,v):
        self._a=v
        self.c=math.sqrt((self._a ** 2) - (self._b ** 2))
        # force the update of the focii
        self.center=self.center
        self._accelerate_calcs()

    @property
    def b(self):
        return self._b
    @b.setter
    def b(self,v):
        self._b=v
        self.c = math.sqrt((self._a ** 2) - (self._b ** 2))
        # force the update of the focii
        self.center=self.center
        self._accelerate_calcs()

    # @property
    # def pos(self):
    #     return self._pos
    # @pos.setter
    # def pos(self,v):
    #     self._pos=v

    @property
    def focus1(self):
        return self._focus1

    # Moves the ellipse to make focus1 match the position pos
    @focus1.setter
    def focus1(self,pos):
        self._focus1=pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta=Pos(dx,dy)
        self._center=pos-delta
        self._focus2=self._center-delta

    @property
    def focus2(self):
        return self._focus2
    @focus2.setter
    def focus2(self,pos):
        self._focus1=pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta=Pos(dx,dy)
        self._center=pos+delta
        self._focus1=self._center+delta

    @property
    def center(self):
        return self._center
    @center.setter
    def center(self,pos):
        self._center=pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta=Pos(dx,dy)
        self._focus1=pos-delta
        self._focus2=pos+delta

    @property
    def incl(self):
        return self._incl
    @incl.setter
    def incl(self,val):
        self._incl=val
        self._accelerate_calcs()
        # forces the update of the focii
        self.center=self.center

    # returns a rectangle in absolute coordinates that contains the orbit
    @property
    def area(self):
        #a2cos2=(self.a**2)*((math.cos(math.radians(self.incl)))**2)
        #b2sin2 = (self.b ** 2) * ((math.sin(math.radians(self.incl))) ** 2)

        a2cos2=self.a2*self.cos2
        b2sin2=self.b2*self.sin2
        x=math.sqrt(a2cos2+b2sin2)

        #a2sin2 = (self.a ** 2) * ((math.sin(math.radians(self.incl))) ** 2)
        #b2cos2 = (self.b ** 2) * ((math.cos(math.radians(self.incl))) ** 2)

        a2sin2=self.a2*self.sin2
        b2cos2 = self.b2 * self.cos2
        y=math.sqrt(a2sin2+b2cos2)

        center=self._center
        left=center.x-x
        top=center.y+y
        width=2*x
        height=2*y
        return Rectangle(left,top,width,height)


    # returns the intersection points of the ellipse with a vertical line in X
    def intersect_points_X(self,x):
        # the formulas assume that the ellipse is centered at (0,0)
        #  so first, we move the vertical line according to the shift
        x-=self.center.x
        # later we need to shift the intersection points

        results=[]
        # a2=self.a**2
        # b2=self.b**2
        # sin=math.sin(math.radians(self.incl))
        # cos = math.cos(math.radians(self.incl))
        # sin2=sin**2
        # cos2=cos**2
        # Intersects vertical, x=K
        A=(self.b2*self.sin2)+(self.a2*self.cos2)
        B=2*x*self.sin*self.cos*(self.b2-self.a2)
        C=(x**2)*((self.b2*self.cos2)+(self.a2*self.sin2))-(self.a2*self.b2)
        sqterm=(B**2)-(4*A*C)
        if sqterm>=0:
            valYmenos=(-B-(math.sqrt(sqterm)))/(2*A)
            results.append(Pos(x+self.center.x,valYmenos+self.center.y))
            valYmas=(-B+(math.sqrt(sqterm)))/(2*A)
            results.append(Pos(x+self.center.x,valYmas+self.center.y))
        return results


    # returns the intersection points of the ellipse with a horizontal line in y
    def intersect_points_Y(self,y):
        y-=self.center.y

        results=[]
        a2=self.a**2
        b2=self.b**2
        sin=math.sin(math.radians(self.incl))
        cos = math.cos(math.radians(self.incl))
        sin2=sin**2
        cos2=cos**2

        # Intersects horizontal, y=K
        A=(b2*cos2)+(a2*sin2)
        B=2*y*sin*cos*(b2-a2)
        C=(y**2)*((a2*cos2)+(b2*sin2))-(a2*b2)
        sqterm=(B**2)-(4*A*C)
        if sqterm>=0:
            valXmas=(-B+math.sqrt(sqterm))/(2*A)
            results.append(Pos(valXmas+self.center.x,y+self.center.y))
            valXmenos=(-B-math.sqrt(sqterm))/(2*A)
            results.append(Pos(valXmenos+self.center.x,y+self.center.y))
        return results

    def intersect_points_with_rect(self,rect):
        pointsx=[]
        ps=self.intersect_points_X(rect.left)
        for p in ps:
            if rect.belongs(p):
                pointsx.append(p)
        ps=self.intersect_points_X(rect.right)
        for p in ps:
            if rect.belongs(p):
                pointsx.append(p)

        pointsy=[]
        ps=self.intersect_points_Y(rect.top)
        for p in ps:
            if rect.belongs(p):
                pointsy.append(p)

        ps=self.intersect_points_Y(rect.bottom)
        for p in ps:
            if rect.belongs(p):
                pointsy.append(p)

        return {'x':pointsx,'y':pointsy}


    # returns a tuple with two paths
    # the paths are the solutions (-/+) of the ellipse for a number of npoints between x1 and x2
    def paths(self,x1,x2,npoints):
        #x1 -= self.center.x
        #x2 -= self.center.x
        path1=[]
        path2=[]
        if (x1>x2):
            (x1,x2)=(x2,x1)
        step=(x2-x1)/npoints

        x=x1
        while x<x2:
            vals=self._y(x)
            if vals:
                #path1.append(Pos(x,vals[0])+self.center)
                #path2.append(Pos(x, vals[1])+self.center)
                path1.append(Pos(x,vals[0]))
                path2.append(Pos(x, vals[1]))

            x+=step
        vals=self._y(x2)
        if vals:
            #path1.append(Pos(x,vals[0])+self.center)
            #path2.append(Pos(x, vals[1])+self.center)
            path1.append(Pos(x, vals[0]))
            path2.append(Pos(x, vals[1]))

        return (path1,path2)

    # def paths(self,x1,x2,npoints):
    #     x1 -= self.center.x
    #     x2 -= self.center.x
    #     path1=[]
    #     path2=[]
    #     if (x1>x2):
    #         (x1,x2)=(x2,x1)
    #     step=(x2-x1)/npoints
    #
    #     a2=self.a**2
    #     b2=self.b**2
    #     sin=math.sin(math.radians(self.incl))
    #     cos = math.cos(math.radians(self.incl))
    #     sin2=sin**2
    #     cos2=cos**2
    #     x=x1
    #     while x<=x2:
    #         A = (b2 * sin2) + (a2 * cos2)
    #         B = 2 * x * sin * cos * (b2 - a2)
    #         C = (x ** 2) * ((b2 * cos2) + (a2 * sin2)) - (a2 * b2)
    #         sqterm = (B ** 2) - (4 * A * C)
    #         if sqterm>=0:
    #             valYmenos = -B - (math.sqrt(sqterm) / (2 * A))
    #             valYmas = -B + (math.sqrt(sqterm) / (2 * A))
    #
    #             path1.append(Pos(x,valYmenos)+self.center)
    #             path2.append(Pos(x, valYmas)+self.center)
    #
    #         x+=step
    #     return (path1,path2)


    def _y(self,x):
        x-=self.center.x
        A = (self.b2 * self.sin2) + (self.a2 * self.cos2)
        B = 2 * x * self.sin * self.cos * (self.b2 - self.a2)
        C = (x ** 2) * ((self.b2 * self.cos2) + (self.a2 * self.sin2)) - (self.a2 * self.b2)
        sqterm = (B ** 2) - (4 * A * C)
        if sqterm >= 0:
            valYmenos = (-B - (math.sqrt(sqterm))) / (2 * A)
            valYmas = (-B + (math.sqrt(sqterm))) / (2 * A)
            return(valYmenos+self.center.y,valYmas+self.center.y)
        else:
            return None





