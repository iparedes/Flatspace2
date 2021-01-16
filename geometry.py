import math


class Error(Exception):
    """Base class for other exceptions"""
    pass


class EccentricityError(Error):
    """Raised when the input value is too small"""
    pass


class Pos:

    # Our space is flat, so we will only use x and y coords
    # we keep z as Pos is also used to define a vector and the cross product of vectors
    # results in a vector perpendicular to the plane x,y
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        # t="("+"{:.2E}".format(self.x)+","+"{:.2E}".format(self.y)+")"
        # t = "(" + str(self.x) + "," + str(self.y) + ")"
        # t = "(" + str(self.x) + "," + str(self.y) + "," +str(self.z)+")"
        t = "(" + f'{self.x:,}' + "," + f'{self.y:,}' + "," + f'{self.z:,}' + ")"
        return t

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y, self.z - other.z)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    # Multiply both coordinates by a value
    def __rmul__(self, value):
        return Pos(self.x * value, self.y * value, self.z * value)

    # Multiply both coordinates by a value
    def __mul__(self, value):
        return Pos(self.x * value, self.y * value, self.z * value)

    def __truediv__(self, value):
        p = Pos(self.x / value, self.y / value, self.z / value)
        return p

    def rotate_rads(self, rads):
        x = (self.x * math.cos(rads)) - (self.y * math.sin(rads))
        y = (self.y * math.cos(rads)) + (self.x * math.sin(rads))
        pos = Pos(x, y)
        return pos

    def rotate(self, degrees):
        p = rotate_rads(math.radians(degrees))
        return p

    def coords(self):
        return (self.x, self.y)

    def coordZ(self):
        return self.z

    def distance(self, other):
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2) + ((self.z - other.z) ** 2))


class Line:
    # possible arguments:
    #   slope ,intercept for y=slope*x+intercept
    #   pos1, pos2 (of type Pos) to create a line between the two points
    def __init__(self, **kwargs):
        if all(k in kwargs for k in ("slope","intercept")):
            self.slope = kwargs['slope']
            self.intercept = kwargs['intercept']
        elif all(k in kwargs for k in ("p1","p2")):
            p1 = kwargs['p1']
            p2 = kwargs['p2']
            a=p2.x-p1.x
            if a==0:
                # vertical line
                self.slope=None
                self.intercept=p1.x
            else:
                b=p2.y-p1.y
                self.slope=b/a
                self.intercept=((p2.x*p1.y)-(p1.x*p2.Y))/(a)
        else:
            raise SyntaxError("arguments in Line")

    def __eq__(self, other):
        if (self.slope==other.slope) and (self.intercept==other.intercept):
            return True
        else:
            return False


    def y(self,x):
        y=(x*self.slope)+self.intercept
        return y

    def x(self,y):
        x=(y-self.intercept)/self.slope
        return x

    # returns 0 or 1 depending to what 'side' of the line the point is
    # if the line is horizontal 0 is above and 1 below
    def side(self,point):
        if (self.slope):
            liney=self.y(point.x)
            if point.y>=liney:
                val=0
            else:
                val=1
        else:
            # vertical line
            if point.x<=self.intercept:
                val=0
            else:
                val=1
        return val

    def intersection(self,line):
        if self==line:
            # same line
            return None
        elif self.slope==line.slope:
            # parallel lines
            return None
        elif self.slope==None:
            # self is vertical
            y=line.y(self.intercept)
            return Pos(self.intercept,y)
        elif line.slope==None:
            # line is vertical
            y=self.y(line.intercept)
            return Pos(line.intercept,y)
        else:
            # two regular lines
            x=(line.intercept-self.intercept)/(self.slope-line.slope)
            y=self.y(x)
            return Pos(x,y)



class Vector(Pos):

    # Constructors
    # Pos
    # x,y
    # magnitud+dir
    def __init__(self, **kwargs):
        if 'pos' in kwargs:
            pos = kwargs['pos']
            Pos.__init__(self, pos.x, pos.y, pos.z)
        elif 'x' and 'y' in kwargs:
            x = kwargs['x']
            y = kwargs['y']
            if 'z' in kwargs:
                z = kwargs['z']
            else:
                z = 0
            Pos.__init__(self, x, y, z)
        else:
            mag = kwargs['magnitud']
            dir = kwargs['dir']
            xp = mag * math.cos(math.radians(dir))
            yp = mag * math.sin(math.radians(dir))
            Pos.__init__(self, xp, yp)

    # needs either a pos (assumes origin at (0,0) or magnitud+dir
    # def __init__(self,pos=Pos(0,0),magnitud=0,dir=0):
    #     if magnitud==0:
    #         Pos.__init__(self,pos.x, pos.y)
    #     else:
    #         xp = magnitud * math.cos(math.radians(dir))
    #         yp = magnitud * math.sin(math.radians(dir))
    #         Pos.__init__(self,xp,yp)

    def __str__(self):
        t = Pos.__str__(self)
        t += "\nMag: " + "{:.2f}".format(self.magnitude) + " Dir: " + "{:.2f}".format(self.direction)
        return t

    def __add__(self, other):
        p = Pos.__add__(self, other)
        return Vector(p)

    def __iadd__(self, other):
        Pos.__iadd__(self, other)
        return self

    def __sub__(self, other):
        p = Pos.__sub__(self, other)
        return Vector(pos=p)

    def __isub__(self, other):
        Pos.__isub__(self, other)
        return self

    # Multiplies vector by scalar
    def __mul__(self, other):
        p = Pos.__rmul__(self, other)
        return Vector(pos=p)

    # Multiplies vector by scalar
    def __rmul__(self, other):
        p = Pos.__rmul__(self, other)
        return Vector(pos=p)

    def __truediv__(self, value):
        p = Pos.__truediv__(self, value)
        return Vector(pos=p)

    @property
    def pos(self):
        return Pos(self.x, self.y)

    @property
    def magnitude(self):
        v = math.sqrt((self.x) ** 2 + (self.y) ** 2 + (self.z) ** 2)
        return v

    # Modifies the magnitud of the vector maintaining the origin
    # careful. Only works in the x,y plane
    @magnitude.setter
    def magnitude(self, v):
        alfa = self.direction_radians
        xp = v * math.cos(alfa)
        yp = v * math.sin(alfa)
        self.x = xp
        self.y = yp

    @property
    def direction(self):
        v = self.direction_radians
        return math.degrees(v)

    @property
    def direction_radians(self):
        if self.x == 0:
            if self.y > 0:
                v = math.pi / 2
            elif self.y < 0:
                v = 3 * math.pi / 2
            else:
                v = 0  # special case where there is no vector (magnitude 0)
        elif self.y == 0:
            if self.x > 0:
                v = 0
            else:  # x<0
                v = math.pi
        else:
            alfa = math.atan(abs(self.y) / abs(self.x))
            if self.x > 0:
                if self.y > 0:
                    v = alfa
                else:
                    v = (2 * math.pi) - alfa
            else:  # x<0
                if self.y > 0:
                    v = math.pi - alfa
                else:
                    v = alfa + math.pi
        return v

    def dot_product(self, other):
        a = (self.x * other.x) + (self.y * other.y) + (self.z * other.z)
        return a

    def cross_product(self, other):
        x = (self.y * other.z) - (self.z * other.y)
        y = (self.z * other.x) - (self.x * other.z)
        z = (self.x * other.y) - (self.y * other.x)
        p = Pos(x, y, z)
        return Vector(pos=p)
        # a=self.magnitude
        # b=other.magnitude
        # alfa=self.angle_radians(other)
        # crossp=a*b*math.sin(alfa)
        # p=Pos(0,0,crossp)
        # return Vector(pos=p)

    def angle_radians(self, other):
        dotp = self.dot_product(other)
        m1 = self.magnitude
        m2 = other.magnitude
        cosalfa = dotp / (m1 * m2)
        alfa = math.acos(cosalfa)
        return alfa

    # returns angle in degrees formed by two vectors
    def angle(self, other):
        r = self.angle_radians(other)
        return math.degrees(r)


# the reference frame for the rectangle is Cartesian
class Rectangle:

    def __init__(self, left, top, width, height):
        self._top = top
        self._left = left
        self._width = width
        self._height = height
        self._center = Pos(int(left + (width / 2)), int(top - (height / 2)))
        self._bottom = self._top - self._height
        self._right = self._left + self._width

        self.border_lines=[]
        #leftline
        self.border_lines.append(Line(slope=None,intercept=self._left))
        #rightline
        self.border_lines.append(Line(slope=None, intercept=self._right))
        #topline
        self.border_lines.append(Line(slope=0, intercept=self._top))
        #bottomline
        self.border_lines.append(Line(slope=0, intercept=self._bottom))


    def __str__(self):
        t = "left:" + str(self.left) + ", top:" + str(self.top) + " -> right:" + str(self.right) + ", bottom:" + str(
            self.bottom)
        return t

    # returns true if the point belongs to the rectangle
    def belongs(self, point):
        return self.left <= point.x <= self.right and self.bottom <= point.y <= self.top

    # returns true if there is overlap between self and other
    # overlap can be that one contains the other or an intersection
    def overlap(self, other):
        res = self.left > other.right or self.right < other.left or \
              self.top < other.bottom or self.bottom > other.top
        return not res

    # returns True if self contains other, but not the other way around
    def contains(self, other):
        res = self.left < other.left and self.right > other.right and \
              self.top > other.top and self.bottom < other.bottom
        return res

    # returns True if other intersects any of the vertical sides of self
    def intersects_X(self, other):
        # first checks if other is horizontally aligned with self (are at a similar height)
        res = False
        if (self.bottom < other.top < self.top) or (self.bottom < other.bottom < self.top):
            # now checks if there is intersection on the vertical sides
            res = (other.left < self.left < other.right) or (other.left < self.right < other.right)
        return res

    def intersects_Y(self, other):
        # first checks if other is verticall aligned with self (are at a similar horizontal position)
        res = False
        if (self.left < other.left < self.right) or (self.left < other.right < self.right):
            # now checks if there is intersection on the vertical sides
            res = (other.bottom < self.top < other.top) or (other.bottom < self.bottom < other.top)
        return res

    def intersects(self, other):
        return self.intersects_X(other) or self.intersects_Y(other)

    @property
    def center(self):
        return self._center

    @center.setter
    # p: tupla (x,y)
    def center(self, p):
        x = p.x
        y = p.y
        self._center = p
        self._left = int(x - (self.width / 2))
        self._top = int(y + (self.height / 2))
        self._right = self._left + self._width
        self._bottom = self._top - self._height

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, v):
        self._left = v
        xc = v + int(self.width / 2)
        self._right = v + self.width
        self._center.x = xc

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, v):
        self._right = v
        xc = v - int(self.width / 2)
        self._left = v - self.width
        self._center.x = xc

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, v):
        self._top = v
        yc = v - int(self._height / 2)
        self._center.y = yc
        self._bottom = v - self._height

    @property
    def bottom(self):
        return self._bottom

    @bottom.setter
    def bottom(self, v):
        self._bottom = v
        yc = v + int(self._height / 2)
        self._center.y = yc
        self._top = v + self._height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, v):
        self._width = v
        self._left = self._center.x - int(v / 2)
        self._right = self._left + self._width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, v):
        self._height = v
        self._top = self._center.y + int(v / 2)
        self._bottom = self._top - self._height

# When creating a conic, need to provide at least one of the reference points (center, focus1, focus2)
# if multiple are provided, precedence is focus1>focus2>center
class Conic:
    def __init__(self, a, e, center=None, focus1=None, focus2=None, incl=0):
        self._incl = incl
        self._a = a
        self._e = e
        self.c = self._e * self._a
        self._b = None

        if all(v is not None for v in [center,focus1,focus2]):
            raise SyntaxError("Conic needs at least a point")

        if center != None:
            self.center = center
        if focus2 != None:
            self.focus2 = focus2
        if focus1 != None:
            self.focus1 = focus1
        # c: distance from center to focus
        # self._accelerate_calcs()

    def _accelerate_calcs(self):
        self.a2 = self.a ** 2
        self.b2 = self.b ** 2
        self.sin = math.sin(math.radians(self.incl))
        self.cos = math.cos(math.radians(self.incl))
        self.sin2 = self.sin ** 2
        self.cos2 = self.cos ** 2

    def __str__(self):
        t = "a: " + str(self._a) + ", b: " + str(self._b) + ", c: " + str(self.c) + "\n"
        t += "center: " + str(self._center) + ", f1: " + str(self._focus1) + "f2: " + str(self._focus2)
        return t

    @property
    # the eccentricity formula is the same for all the conics,
    # however, c is calculated in different ways
    def e(self):
        return self.c/self._a

    @property
    def incl(self):
        return self._incl

    # Modifications to the inclination take the center as the rotating point
    # if used for orbits you'll probably want to update the focus afterwards
    @incl.setter
    def incl(self, val):
        self._incl = val
        self._accelerate_calcs()
        # forces the update of the focii
        self.center = self.center


    def intersect_points_with_rect(self, rect):
        pointsx = []
        ps = self.intersect_points_X(rect.left)
        for p in ps:
            if rect.belongs(p):
                pointsx.append(p)
        ps = self.intersect_points_X(rect.right)
        for p in ps:
            if rect.belongs(p):
                pointsx.append(p)

        pointsy = []
        ps = self.intersect_points_Y(rect.top)
        for p in ps:
            if rect.belongs(p):
                pointsy.append(p)

        ps = self.intersect_points_Y(rect.bottom)
        for p in ps:
            if rect.belongs(p):
                pointsy.append(p)

        return {'x': pointsx, 'y': pointsy}


class Hyperbola(Conic):

    # a:semi-major axis
    # b:semi-minor axis
    # c: distance from center to focii
    # e: eccentricity
    # focus1: Pos of the left focus (the one to the left of the center when incl=0)
    # focus2: Pos of the right focus (the one to the right of the center when incl=0)
    # Note that the focii location is different to the ellipse
    def __init__(self, a, e, center=None, focus1=None, focus2=None, incl=0):
        if e < 1:
            raise Exception("Eccentricity Error")
        Conic.__init__(self, a=a, e=e, center=center, focus1=focus1, focus2=focus2, incl=incl)
        # self._b=self._a*math.sqrt((self._e**2)-1)
        self._b = math.sqrt((self.c ** 2) - (self._a ** 2))
        # semi-latus rectum
        self.l=self._semilatus
        self._accelerate_calcs()

    @property
    def a(self):
        return self._a

    # modifies the semi-major axis maintaining the eccentricity
    @a.setter
    def a(self, v):
        self._a = v
        # self.c=math.sqrt((self._a ** 2) - (self._b ** 2))
        self.c = self._a * self._e
        self._b = math.sqrt((self._c ** 2) - (self.a ** 2))
        self.l = self._semilatus
        # force the update of the focii
        self.center = self.center
        self._accelerate_calcs()

    @property
    def b(self):
        return self._b

    # modifies the semi-minor axis maintaining the eccentricity
    @b.setter
    def b(self, v):
        self._b = v
        self._a = self._b / math.sqrt((self._e ** 2) - 1)
        # self.c = math.sqrt((self._a ** 2) - (self._b ** 2))
        self.c = self._a * self._e
        self.l = self._semilatus
        # force the update of the focii
        self.center = self.center
        self._accelerate_calcs()

    @property
    def _semilatus(self):
        l=(self.b**2)/self.a
        return l

    @property
    def focus1(self):
        return self._focus1

    # Moves the hyperbola to make focus1 match the position pos
    @focus1.setter
    def focus1(self, pos):
        self._focus1 = pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta = Pos(dx, dy)
        self._center = pos + delta
        self._focus2 = self._center + delta

    @property
    def focus2(self):
        return self._focus2

    @focus2.setter
    def focus2(self, pos):
        self._focus1 = pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta = Pos(dx, dy)
        self._center = pos - delta
        self._focus1 = self._center - delta

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, pos):
        self._center = pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta = Pos(dx, dy)
        self._focus1 = pos + delta
        self._focus2 = pos - delta


    @property
    # returns Pos of vertex closer to focus1
    def v1(self):
        x = self.center.x
        y = self.center.y
        vx = x + (self.a * math.cos(math.radians(self.incl)))
        vy = y + (self.a * math.sin(math.radians(self.incl)))
        return (Pos(vx, vy))

    @property
    # returns Pos of vertex closer to focus2
    def v2(self):
        x = self.center.x
        y = self.center.y
        vx = x - (self.a * math.cos(math.radians(self.incl)))
        vy = y - (self.a * math.sin(math.radians(self.incl)))
        return (Pos(vx, vy))

    def asymptote1(self):
        # Need to account for the inclination of the hyperbola
        d=math.sqrt((self.a**2)+(self.b**2))
        beta=math.atan(self.b/self.a)
        angle=beta+math.radians(self.incl)
        newa=d*math.cos(angle)
        newb = d * math.sin(angle)

        slope=newb/newa
        inter=self.center.y-(slope*self.center.x)

        l=Line(slope=slope,intercept=inter)
        return l

    def asymptote2(self):
        # Need to account for the inclination of the hyperbola
        d=math.sqrt((self.a**2)+(self.b**2))
        beta=math.atan(self.b/self.a)
        angle=beta-math.radians(self.incl)
        newa=d*math.cos(angle)
        newb = d * math.sin(angle)

        slope=-newb/newa
        inter = self.center.y - (slope * self.center.x)

        l=Line(slope=slope,intercept=inter)
        return l

    # returns the intersection points of the hyperbola with a vertical line in X
    def intersect_points_X(self, x):
        # the formulas assume that the ellipse is centered at (0,0)
        #  so first, we move the vertical line according to the shift
        x -= self.center.x
        # later we need to shift the intersection points

        results = []

        # Intersects vertical, x=K
        A = (self.b2 * self.sin2) - (self.a2 * self.cos2)
        B = 2 * x * self.sin * self.cos * (self.b2 + self.a2)
        C = (x ** 2) * ((self.b2 * self.cos2) - (self.a2 * self.sin2)) - (self.a2 * self.b2)
        sqterm = (B ** 2) - (4 * A * C)
        if sqterm >= 0:
            valYmenos = (-B - (math.sqrt(sqterm))) / (2 * A)
            results.append(Pos(x + self.center.x, valYmenos + self.center.y))
            valYmas = (-B + (math.sqrt(sqterm))) / (2 * A)
            results.append(Pos(x + self.center.x, valYmas + self.center.y))
        return results

    # returns the intersection points of the hyperbola with a horizontal line in y
    def intersect_points_Y(self, y):
        y -= self.center.y

        results = []
        a2 = self.a ** 2
        b2 = self.b ** 2
        sin = math.sin(math.radians(self.incl))
        cos = math.cos(math.radians(self.incl))
        sin2 = sin ** 2
        cos2 = cos ** 2

        # Intersects horizontal, y=K
        A = (b2 * cos2) - (a2 * sin2)
        B = 2 * y * sin * cos * (b2 + a2)
        C = (y ** 2) * ((b2 * sin2) - (a2 * cos2)) - (a2 * b2)
        sqterm = (B ** 2) - (4 * A * C)
        if sqterm >= 0:
            valXmas = (-B + math.sqrt(sqterm)) / (2 * A)
            results.append(Pos(valXmas + self.center.x, y + self.center.y))
            valXmenos = (-B - math.sqrt(sqterm)) / (2 * A)
            results.append(Pos(valXmenos + self.center.x, y + self.center.y))
        return results

    def paths_0ld2(self, x1, x2, npoints):
        vertx = self.v2.x
        if (x1 > x2):
            (x1, x2) = (x2, x1)
        step = (x2 - x1) / npoints
        top = []
        tail = []
        x = x1
        while x < vertx:
            vals = self._y(x)
            if vals:
                top.append(Pos(x, vals[0]))
                tail.insert(0, Pos(x, vals[1]))
            x += step

        valsy = self._y(vertx)
        top.append(Pos(vertx, valsy[0]))
        tail.insert(0, Pos(vertx, valsy[1]))
        path1 = top + tail
        top = []
        tail = []

        vertx = self.v1.x
        valsy = self._y(vertx)
        # top.append(Pos(x, valsy[0]))
        # tail.insert(0, Pos(x, valsy[1]))
        x = vertx
        while x <= x2:
            vals = self._y(x)
            if vals:
                top.append(Pos(x, vals[0]))
                tail.insert(0, Pos(x, vals[1]))
            x += step
        path2 = top + tail
        return (path1, path2)

    # returns a tuple with two paths
    # each path has a side of the hyperbola for a number of npoints between x1 and x2
    def paths_old(self, x1, x2, npoints):
        # x1 -= self.center.x
        # x2 -= self.center.x
        top1 = []
        tail1 = []
        top2 = []
        tail2 = []

        if (x1 > x2):
            (x1, x2) = (x2, x1)
        step = (x2 - x1) / npoints

        middle = self.center.x
        x = x1
        if x < middle:
            activepath = [top1, tail1]
        else:
            activepath = [top2, tail2]

        while x < x2:
            vals = self._y(x)
            if vals:
                # path1.append(Pos(x,vals[0])+self.center)
                # path2.append(Pos(x, vals[1])+self.center)

                # path1.append(Pos(x,vals[0]))
                # path2.append(Pos(x, vals[1]))
                # activepath[0].append(Pos(x,vals[0]))
                # activepath[1].append(Pos(x, vals[1]))
                activepath[0].append(Pos(x, vals[0]))
                activepath[1].insert(0, Pos(x, vals[1]))

            x += step
            if x < middle:
                activepath = [top1, tail1]
            else:
                activepath = [top2, tail2]

        vals = self._y(x2)
        if vals:
            # path1.append(Pos(x,vals[0])+self.center)
            # path2.append(Pos(x, vals[1])+self.center)
            # path1.append(Pos(x, vals[0]))
            # path2.append(Pos(x, vals[1]))
            # activepath[0].append(Pos(x, vals[0]))
            # activepath[1].append(Pos(x, vals[1]))

            activepath[0].append(Pos(x, vals[0]))
            activepath[1].insert(0, Pos(x, vals[1]))

        path1 = top1 + tail1
        path2 = top2 + tail2
        return (path1, path2)

    # returns the two archs that compose the hyperbola
    # if pos is different than None, it only returns the closest arch
    # (used to obtain an orbital path)
    def paths(self, x1, x2, npoints):
        path1 = []
        path2 = []
        asymptote=self.asymptote1()

        if (x1 > x2):
            (x1, x2) = (x2, x1)
        step = (x2 - x1) / npoints

        x = x1
        while x <= x2:
            vals = self._y(x)
            if vals:
                v1=vals[0]
                v2=vals[1]
                pos1=Pos(x,v1)
                pos2=Pos(x,v2)
                side1 = asymptote.side(pos1)
                side2 = asymptote.side(pos2)

                if side1==side2:
                    # pos1 and pos2 are in opposite ends of the arch segment
                    # e.g. vertical hyperbola
                    if side1==0:
                        active=path1
                    else:
                        active=path2
                    midpoint=len(active)//2
                    t=[pos1,pos2]
                    active[midpoint:midpoint]=t
                else:
                    # pos1 and pos2 are in different arch segments
                    # e.g. horizontal hyperbola
                    if side1==0:
                        path1.append(pos1)
                        path2.append(pos2)
                    else:
                        path1.append(pos2)
                        path2.append(pos1)
            x += step
        if self.incl==0:
            #vertical asymptote
            path1.sort(key=lambda p: p.y)
            path2.sort(key=lambda p: p.y)

        return (path1, path2)

    def _y(self, x):
        x -= self.center.x
        A = (self.b2 * self.sin2) - (self.a2 * self.cos2)
        B = 2 * x * self.sin * self.cos * (self.b2 + self.a2)
        C = (x ** 2) * ((self.b2 * self.cos2) - (self.a2 * self.sin2)) - (self.a2 * self.b2)
        sqterm = (B ** 2) - (4 * A * C)
        if sqterm >= 0:
            valYmenos = (-B - (math.sqrt(sqterm))) / (2 * A)
            valYmas = (-B + (math.sqrt(sqterm))) / (2 * A)
            return (valYmenos + self.center.y, valYmas + self.center.y)
        else:
            return None


class Ellipse(Conic):
    # a:semi-major axis
    # b:semi-minor axis
    # c: distance from center to focii
    # center: Pos, center of the ellipse
    # focus1: Pos of the right focus (the one to the right of the center when incl=0)
    # focus2: Pos of the left focus (the one to the left of the center when incl=0)
    # incl: in degrees, counterclockwise from the X axis
    def __init__(self, a, e, center=None, focus1=None, focus2=None, incl=0):
        if e >= 1:
            raise Exception("Eccentricity Error")
        Conic.__init__(self, a=a, e=e, center=center, focus1=focus1, focus2=focus2, incl=incl)
        # self._b=self._a*math.sqrt(1-(self._e**2))
        self._b = math.sqrt((self._a ** 2) - (self.c ** 2))
        # semi-latus rectum
        self.l=self._semilatus
        self._accelerate_calcs()

    @property
    def a(self):
        return self._a

    # modifies the semi-major axis maintaining the eccentricity
    @a.setter
    def a(self, v):
        self._a = v
        # self.c=math.sqrt((self._a ** 2) - (self._b ** 2))
        self.c = self._a * self._e
        self._b = math.sqrt((self._a ** 2) - (self.c ** 2))
        # updates the semi-latus
        self.l = self._semilatus
        # force the update of the focii
        self.center = self.center
        self._accelerate_calcs()

    @property
    def b(self):
        return self._b

    # modifies the semi-minor axis maintaining the eccentricity
    @b.setter
    def b(self, v):
        self._b = v
        self._a = self._b / math.sqrt(1 - (self._e ** 2))
        # self.c = math.sqrt((self._a ** 2) - (self._b ** 2))
        self.c = self._a * self._e
        # updates the semi-latus
        self.l = self._semilatus
        # force the update of the focii
        self.center = self.center
        self._accelerate_calcs()

    @property
    def _semilatus(self):
        l=self.a*(1-(self.e**2))
        return l

    @property
    def focus1(self):
        return self._focus1

    # Moves the ellipse to make focus1 match the position pos
    @focus1.setter
    def focus1(self, pos):
        self._focus1 = pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta = Pos(dx, dy)
        self._center = pos - delta
        self._focus2 = self._center - delta

    @property
    def focus2(self):
        return self._focus2

    @focus2.setter
    def focus2(self, pos):
        self._focus1 = pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta = Pos(dx, dy)
        self._center = pos + delta
        self._focus1 = self._center + delta

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, pos):
        self._center = pos
        dy = self.c * math.sin(math.radians(self.incl))
        dx = self.c * math.cos(math.radians(self.incl))
        delta = Pos(dx, dy)
        self._focus1 = pos - delta
        self._focus2 = pos + delta


    # returns a rectangle in absolute coordinates that contains the ellipse
    @property
    def area(self):
        # a2cos2=(self.a**2)*((math.cos(math.radians(self.incl)))**2)
        # b2sin2 = (self.b ** 2) * ((math.sin(math.radians(self.incl))) ** 2)

        a2cos2 = self.a2 * self.cos2
        b2sin2 = self.b2 * self.sin2
        x = math.sqrt(a2cos2 + b2sin2)

        # a2sin2 = (self.a ** 2) * ((math.sin(math.radians(self.incl))) ** 2)
        # b2cos2 = (self.b ** 2) * ((math.cos(math.radians(self.incl))) ** 2)

        a2sin2 = self.a2 * self.sin2
        b2cos2 = self.b2 * self.cos2
        y = math.sqrt(a2sin2 + b2cos2)

        center = self._center
        left = center.x - x
        top = center.y + y
        width = 2 * x
        height = 2 * y
        return Rectangle(left, top, width, height)

    # returns the intersection points of the ellipse with a vertical line in X
    def intersect_points_X(self, x):
        # the formulas assume that the ellipse is centered at (0,0)
        #  so first, we move the vertical line according to the shift
        x -= self.center.x
        # later we need to shift the intersection points

        results = []
        # a2=self.a**2
        # b2=self.b**2
        # sin=math.sin(math.radians(self.incl))
        # cos = math.cos(math.radians(self.incl))
        # sin2=sin**2
        # cos2=cos**2
        # Intersects vertical, x=K
        A = (self.b2 * self.sin2) + (self.a2 * self.cos2)
        B = 2 * x * self.sin * self.cos * (self.b2 - self.a2)
        C = (x ** 2) * ((self.b2 * self.cos2) + (self.a2 * self.sin2)) - (self.a2 * self.b2)
        sqterm = (B ** 2) - (4 * A * C)
        if sqterm >= 0:
            valYmenos = (-B - (math.sqrt(sqterm))) / (2 * A)
            results.append(Pos(x + self.center.x, valYmenos + self.center.y))
            valYmas = (-B + (math.sqrt(sqterm))) / (2 * A)
            results.append(Pos(x + self.center.x, valYmas + self.center.y))
        return results

    # returns the intersection points of the ellipse with a horizontal line in y
    def intersect_points_Y(self, y):
        y -= self.center.y

        results = []
        a2 = self.a ** 2
        b2 = self.b ** 2
        sin = math.sin(math.radians(self.incl))
        cos = math.cos(math.radians(self.incl))
        sin2 = sin ** 2
        cos2 = cos ** 2

        # Intersects horizontal, y=K
        A = (b2 * cos2) + (a2 * sin2)
        B = 2 * y * sin * cos * (b2 - a2)
        C = (y ** 2) * ((a2 * cos2) + (b2 * sin2)) - (a2 * b2)
        sqterm = (B ** 2) - (4 * A * C)
        if sqterm >= 0:
            valXmas = (-B + math.sqrt(sqterm)) / (2 * A)
            results.append(Pos(valXmas + self.center.x, y + self.center.y))
            valXmenos = (-B - math.sqrt(sqterm)) / (2 * A)
            results.append(Pos(valXmenos + self.center.x, y + self.center.y))
        return results

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

    # returns a tuple with two paths
    # the paths are the solutions (-/+) of the ellipse for a number of npoints between x1 and x2
    def paths(self, x1, x2, npoints):
        # x1 -= self.center.x
        # x2 -= self.center.x
        path1 = []
        path2 = []
        if (x1 > x2):
            (x1, x2) = (x2, x1)
        step = (x2 - x1) / npoints

        x = x1
        while x < x2:
            vals = self._y(x)
            if vals:
                # path1.append(Pos(x,vals[0])+self.center)
                # path2.append(Pos(x, vals[1])+self.center)
                path1.append(Pos(x, vals[0]))
                path2.append(Pos(x, vals[1]))

            x += step
        vals = self._y(x2)
        if vals:
            # path1.append(Pos(x,vals[0])+self.center)
            # path2.append(Pos(x, vals[1])+self.center)
            path1.append(Pos(x, vals[0]))
            path2.append(Pos(x, vals[1]))

        return (path1, path2)

    def _y(self, x):
        x -= self.center.x
        A = (self.b2 * self.sin2) + (self.a2 * self.cos2)
        B = 2 * x * self.sin * self.cos * (self.b2 - self.a2)
        C = (x ** 2) * ((self.b2 * self.cos2) + (self.a2 * self.sin2)) - (self.a2 * self.b2)
        sqterm = (B ** 2) - (4 * A * C)
        if sqterm >= 0:
            valYmenos = (-B - (math.sqrt(sqterm))) / (2 * A)
            valYmas = (-B + (math.sqrt(sqterm))) / (2 * A)
            return (valYmenos + self.center.y, valYmas + self.center.y)
        else:
            return None
