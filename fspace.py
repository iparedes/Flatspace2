import math
from geometry import *

G = 6.674E-11  # m•k-1•s-2.

# everything in the universe (planets, ships, ...)
class Body:
    def __init__(self,primary=None,name="",mass=0,pos=None):
        self.name=name
        self.primary=primary    # body that is in the center of the orbit
        self.orbit=None         # orbit around the primary body
        self.satellites=[]      # orbiting bodies
        self._pos = pos
        self.mass=mass
        self.time=0             # time after periapsis

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self,p):
        self._pos=p
        #todo Needs to update the positions (focus) of the orbits of all satellites

    @property
    # returns the area of flatspace that the element is occupying
    def area(self):
        return None

    # gives the position of the body in the orbit and the time after periapisis (seconds)
    # at a given angle of the true anomaly
    def pos_at_angle(self, angle):
        # angle is the alfa. True anomaly. 0 degrees is at periapsis
        # orbit.incl is the theta
        alfa = math.radians(angle)
        sinalfa = math.sin(alfa)
        cosalfa = math.cos(alfa)
        a = self.orbit.a
        b = self.orbit.b
        sintheta = self.orbit._sintheta
        costheta = self.orbit._costheta

        x = int((a * cosalfa * costheta) - (b * sinalfa * sintheta))
        y = int((a * cosalfa * sintheta) + (b * sinalfa * costheta))

        Q = Pos(x, y)
        pos = Q + self.orbit.center

        # time after periapsis
        time=(self.T*alfa)/(2*math.pi)

        return (pos,time)

    # all the crap about the anomalies HAS to be relative to the orbit, no absolute values

    # sets the pos of the body according to the time (in seconds) since the periapsis
    def set_pos_time(self, t):
        # E is the (angle) eccentric anomaly t seconds after the periapsis
        E = (t * 2 * math.pi) / self.T
        # calculate the position of E without accounting for the orbit inclination
        x = self.orbit.a * math.cos(E)
        y = self.orbit.a * math.sin(E)
        # calculate the position of the true anomaly
        # x is the same
        y = y * (self.orbit.b / self.orbit.a)

        # account for the inclination of the orbit
        beta = math.radians(self.orbit.incl)
        newx = (x * math.cos(beta)) - (y * math.sin(beta))
        newy = (y * math.cos(beta)) + (x * math.sin(beta))
        x = self.orbit.center.x + newx
        y = self.orbit.center.y + newy
        pos = Pos(x, y)
        self.pos = pos
        self.time = t
        return pos

    def get_eccentric_anomaly_pos(self):
        # get the pos of eccentric anomaly
        y = self.pos.x * (self.orbit.a / self.orbit.b)
        E = Pos(x, y)
        return E

    # returns the angle of the true anomaly (in degrees)
    def get_true_anomaly(self):
        # calculates distance from the current position to the focus
        d = self.pos.distance(self.orbit.focus1)
        # the sin of the true anomaly is the y coord over the distance
        nu = math.asin(self.pos.y / d)
        return math.radians(nu)

    # updates the pos of the body in the orbit according to a delta in seconds
    def update_pos(self,delta):
        self.set_pos_time(self.time+delta)

class Sun(Body):
    def __init__(self, name="", mass=0, pos=None, radius=0):
        Body.__init__(self,primary=None,name=name,mass=mass,pos=pos)
        self.radius=radius
        self.orbit=None
        self.pos=Pos(0,0)

    def add_planet(self, planet):
        self.satellites.append(planet)

    @property
    def area(self):
        left = self.pos.x - self.radius
        top = self.pos.y + self.radius
        width = self.radius * 2
        height = width
        R = Rectangle(left, top, width, height)
        return R

class Planet(Body):
    def __init__(self, primary=None, name="", mass=0, radius=0,peri=0,apo=0,incl=0,init_pos=0):
        Body.__init__(self,primary=primary,name=name,mass=mass)
        self.radius=radius
        self.orbit=Orbit(primary.pos,peri,apo,incl)
        self.T = 0  # Orbital period
        self.T = (2 * math.pi) * math.sqrt(self.orbit.a ** 3 / (G * self.primary.mass))
        (self.pos,self.time)=self.pos_at_angle(init_pos)

    def __str__(self):
        t=self.name+" mass:"+"{:.2e}".format(self.mass)+" radius: "+"{:.2e}".format(self.radius)+"\nOrbit: "+str(self.orbit)
        return t

    @property
    def area(self):
        left = self.pos.x - self.radius
        top = self.pos.y + self.radius
        width = self.radius * 2
        height = width
        R = Rectangle(left, top, width, height)
        return R


class Orbit():
    # focus1 is the position of focus1
    def __init__(self, focus1=None, peri=0, apo=0, incl=0):
        if (peri > apo):
            (peri, apo) = (apo, peri)


        # Where should I put the incl attribute, in the orbit, or in the ellipse inside the orbit?
        self.peri = peri
        self.apo = apo

        # a: semi-major axis
        # b: semi-minor axis
        # c: distance from center to focus
        self.a = (self.peri + self.apo) / 2
        self.c = self.a - self.peri
        self.b = int(math.sqrt((self.a ** 2) - (self.c ** 2)))
        self.ellipse=Ellipse(self.a,self.b,focus1=focus1,incl=incl)

        # to accelerate calculations
        self._costheta = math.cos(math.radians(incl))
        self._sintheta = math.sin(math.radians(incl))

    def __str__(self):
        t="a:"+"{:.2e}".format(self.a)+", "+"b:"+"{:.2e}".format(self.b)+"\n"
        r=self.area
        t+="top:"+"{:.2e}".format(r.top)+", left:"+"{:.2e}".format(r.left)+", bottom:"+"{:.2e}".format(r.bottom)+", right:"+"{:.2e}".format(r.right)+"\n"
        return t

    @property
    def focus(self):
        return self.ellipse.focus1

    @property
    def center(self):
        return self.ellipse.center

    @property
    def area(self):
        return self.ellipse.area

    @property
    def incl(self):
        return self.ellipse.incl
    @incl.setter
    def incl(self,val):
        self.ellipse.incl=val

class SSystem:
    def __init__(self):
        self.Sol = Sun()
        self.epoch=0
        self.days=0

    def update(self,delta):
        self.epoch+=delta
        print("delta: "+str(delta))
        if(self.epoch/86400>self.days):
            self.days+=1
            print(str(self.days)+" days")
        for p in self.Sol.satellites:
            p.update_pos(delta)
