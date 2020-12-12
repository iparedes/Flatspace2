import math
from geometry import *
from itertools import chain
from copy import copy, deepcopy

G = 6.674E-11  # m3•k-1•s-2.

# everything in the universe (planets, ships, ...)
class Body:
    def __init__(self,primary=None,name="",mass=0,pos=None):
        self.name=name
        self.primary=primary    # The body generating the applicable sphere of influence
        self.orbit=None         # orbit around the primary body
        self.satellites=[]      # orbiting bodies
        self._pos = pos
        self.mass=mass
        self.time=0             # time after periapsis

    def __iter__(self):
        yield self
        for v in chain(*map(iter, self.satellites)):
          yield v

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self,p):
        self._pos=p
        for s in self.satellites:
            s.orbit.focus=p

    @property
    # returns the area of flatspace that the element is occupying
    def area(self):
        return None

    # returns the object (itself or a satellite) identified by ident

    def find(self,ident):
        object=None
        if ident.lower()==self.name.lower():
            object=self
        else:
            for s in self.satellites:
                object=s.find(ident)
                if object:
                    break
        return object

    #fixme This uses self.T that is not defined
    #
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
    #fixme This uses self.T that is not defined. It is defined in the class Planet
    #
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

    #fixme. This is only valid for elliptical orbits
    def get_eccentric_anomaly_pos(self):
        # get the pos of eccentric anomaly
        y = self.pos.x * (self.orbit.a / self.orbit.b)
        E = Pos(x, y)
        return E

    # fixme. This is only valid for elliptical orbits
    # returns the angle of the true anomaly (in degrees)
    def get_true_anomaly(self):
        # calculates distance from the current position to the focus
        d = self.pos.distance(self.orbit.focus1)
        # the sin of the true anomaly is the y coord over the distance
        nu = math.asin(self.pos.y / d)
        return math.radians(nu)

    # updates the pos of the body in the orbit according to a delta in seconds
    # it only accounts for one level of satellites. Probably should use the iterator here
    def update_pos(self,delta):
        self.set_pos_time(self.time+delta)
        for s in self.satellites:
            s.set_pos_time(self.time+delta)

    def add_satellite(self,s):
        self.satellites.append(s)

class Sun(Body):
    def __init__(self, name="", mass=0, pos=None, radius=0):
        Body.__init__(self,primary=None,name=name,mass=mass,pos=pos)
        self.radius=radius
        self.orbit=None
        self.pos=Pos(0,0)

    def add_planet(self, planet):
        self.add_satellite(planet)

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
        self.orbit=Orbit(self.name,primary.pos,peri,apo,incl)
        self.T = 0  # Orbital period
        self.T = (2 * math.pi) * math.sqrt(self.orbit.a ** 3 / (G * self.primary.mass))
        (self.pos,self.time)=self.pos_at_angle(init_pos)
        self.SOI=self.orbit.a*((self.mass/primary.mass)**(2/5))

    def __str__(self):
        t=self.name+" mass:"+"{:.2e}".format(self.mass)+" radius: "+"{:.2e}".format(self.radius)+"\n"
        t+="SOI: "+"{:.2E}".format(self.SOI)+" Orbit: "+str(self.orbit)
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
    def __init__(self, name="",focus1=None, peri=0, apo=0, incl=0):
        if (peri > apo):
            (peri, apo) = (apo, peri)

        self.name=name
        # Where should I put the incl attribute, in the orbit, or in the ellipse inside the orbit?
        self.peri = peri
        self.apo = apo

        # a: semi-major axis
        # b: semi-minor axis
        # c: distance from center to focus
        self.a = (self.peri + self.apo) / 2
        self.c = self.a - self.peri
        self.b = int(math.sqrt((self.a ** 2) - (self.c ** 2)))

        # eccentricity
        e=math.sqrt(1-((self.b**2)/(self.a**2)))
        if e<1:
            self.orbital_path=Ellipse(self.a, e, focus1=focus1, incl=incl)
        else:
            self.orbital_path = Hyperbola(self.a, e, focus1=focus1, incl=incl)

        # to accelerate calculations
        self._costheta = math.cos(math.radians(incl))
        self._sintheta = math.sin(math.radians(incl))

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __str__(self):
        t="a:"+"{:.2e}".format(self.a)+", "+"b:"+"{:.2e}".format(self.b)+"\n"
        r=self.area
        t+="top:"+"{:.2e}".format(r.top)+", left:"+"{:.2e}".format(r.left)+", bottom:"+"{:.2e}".format(r.bottom)+", right:"+"{:.2e}".format(r.right)+"\n"
        return t

    @property
    def focus(self):
        return self.orbital_path.focus1
    @focus.setter
    def focus(self,pos):
        self.orbital_path.focus1=pos

    @property
    def center(self):
        return self.orbital_path.center

    @property
    def area(self):
        return self.orbital_path.area

    @property
    def incl(self):
        return self.orbital_path.incl
    @incl.setter
    def incl(self,val):
        self.orbital_path.incl=val

class SSystem:
    def __init__(self):
        self.Sol = Sun()
        self.epoch=0
        self.days=0
        self.ships=[]
        self.projecting=False

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    # updates delta seconds
    def update(self,delta,projection=False):
        self.epoch+=delta
        if(self.epoch/86400>self.days):
            self.days+=1

        # Planets and satellites go on rails, we can forecast
        for p in self.Sol.satellites:
            p.update_pos(delta)

        # todo this is wrong. Should be done as part of the ship update
        # updates the SOI of ships
        for s in self.ships:
            p=s.pos
            prim = self.soi_body(p)
            if prim != s.primary:
                s.primary = prim

        # if the delta is to big, we are more granular on the ship updates
        # parameters here are:
        #   threshold for the ship calculation
        #   delta for the ship updates
        if delta>=600 and not projection:
            cont=0
            while cont<=delta:
                for s in self.ships:
                    s.update_pos(10)
                cont+=10
        else:
            for s in self.ships:
                print("Updating ship"+s.name)
                s.update_pos(delta)
                print(s.pos)

    def soi_body(self,pos):
        body=None
        # finds if pos is under the SOI of a planet
        for b in self.Sol.satellites:
            d=pos.distance(b.pos)
            if d<b.SOI:
                body=b
                break
        if body:
            # if found a planet, finds if pos is under the SOI of a satellite of the planet
            for b in body.satellites:
                d=pos.distance(b.pos)
                if d<b.SOI:
                    body=b
                    break
        else:
            body=self.Sol
        return body

    # returns the body identified by ident
    def find(self,ident):
        body=self.Sol.find(ident)
        if not body:
            l=[n.name for n in self.ships]
            if ident in l:
                i=l.index(ident)
                body=self.ships[i]
            else:
                body=None
        return body

    # Makes a simulation of the system days ahead of its current time
    def project(self,days):
        self.projecting = True
        step=10800
        cont=step
        max=days*86400
        while cont<=max:
            self.update(step,True)
            cont+=step
            print("project "+str(cont))
        self.projecting = False

    def project_ships(self):
        for s in self.ships:
            (a, b, e, peri, apo, incl) = s.orbital_params()
            if e<1:
                o=Orbit(focus1=s.primary.pos,peri=peri,apo=apo,incl=incl)
                s.orbit=o
            if e>1:
                pass

# A body that is not on rails
class Ship:
    def __init__(self,primary=None,name="",mass=0,pos=Pos(0,0),vel=None):
        self.primary=primary
        self.name=name
        self.mass=mass
        self.pos=pos
        if vel==None:
            self.velocity=Vector(pos=Pos(0,0))
        else:
            self.velocity=vel

        # Projection
        self.path=[]
        self.orbit=None

    def __str__(self):
        t=self.name+" ("+str(self.mass)+"Kg)\n"
        t+="Primary: "+self.primary.name+"\n"
        t+="Pos: "+str(self.pos)+"\n"
        t+="Vel: "+str(self.velocity)
        return t

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def update_pos(self,delta):
        # Calculates the magnitud of the gravitational force
        f=self.Fg()
        # the vector has origin in the ship and points to the center of the primary
        # all our vectors have origin at (0,0) so we calculate de vector at (0,0) that
        # has the right magnitude and direction
        pos=self.primary.pos-self.pos
        vector=Vector(pos=pos)
        vector.magnitude=f
        self.velocity+=vector
        shift=Pos(self.velocity.x*delta,self.velocity.y*delta)
        self.pos+=shift
        newpos=deepcopy(self.pos)
        self.path.append(newpos)
        #print(self.velocity)

    def Fg(self):
        d=self.pos.distance(self.primary.pos)
        f=G*(self.primary.mass/(d**2))
        return f

    @property
    def area(self):
        # todo: by now all ships have 10x10m
        side=10
        left = self.pos.x - side
        top = self.pos.y + side
        width = side
        height = width
        R = Rectangle(left, top, width, height)
        return R

    # From: https://github.com/cmaureir/python-kepler/blob/master/KeplerianOrbit.py
    def orbital_params(self):
        mu=self.primary.mass*G

        # angular momentum
        # j = r x v
        posVector=Vector(pos=self.pos)
        jv=posVector.cross_product(self.velocity)
        # Rung-Lez vector
        # e = { (v x j) / (G * m) }  - { r / |r| }
        tv=self.velocity.cross_product(jv)
        tv=tv/mu
        rv=Vector(pos=self.pos)
        rmag=rv.magnitude
        vv=rv/rmag
        ev=tv-vv

        # ev points (I believe) in the direction of the simmetry axis of the ellipse
        horizontal=Vector(pos=Pos(1,0))
        incl=ev.angle(horizontal)
        print("incl:",incl)

        # Eccentricity
        ecc=ev.magnitude
        print("ecc: "+str(ecc))
        # semi-major axis
        # a = ( j * j ) / (G * m * | 1 - ecc^2 | )
        k=jv.dot_product(jv)
        factor=abs(1-(ecc**2))
        a=k/(mu*factor)
        print("a: "+str(a))

        # semi-minor axis
        b=a*math.sqrt(factor)
        print("b: "+str(b))

        # c: distance from center to focus
        c=a*ecc
        peri=a-c
        apo=a+c

        return(a,b,ecc,peri,apo,incl)










