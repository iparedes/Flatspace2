import math
from geometry import *
from itertools import chain
from copy import copy, deepcopy

G = 6.674E-11  # m3•k-1•s-2.
NEWTON_THRESHOLD=0.01 # Value used to check the convergence on Newton method to solve Kepler eq

# everything in the universe (planets, ships, ...)
class Body:
    def __init__(self,primary=None,name="",mass=0,pos=None):
        self.name=name
        self._primary=primary    # The body generating the applicable sphere of influence
        self.orbit=None         # orbit around the primary body
        self.satellites=[]      # orbiting bodies
        self._pos = pos
        self.mass=mass
        self._time=0             # time after periapsis

    @property
    def primary(self):
        return self._primary
    @primary.setter
    def primary(self,p):
        self._primary=p

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
    def time(self):
        return self._time
    @time.setter

    # Uberimportant. An update of the time (time after the periapsis), sets the pos
    #  of the body accordingly
    def time(self,t):
        self._time=t
        self.pos=self.orbit.get_pos_time(t)

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

    # updates the pos of the body in the orbit according to a delta in seconds
    # it only accounts for one level of satellites. Probably should use the iterator here
    def update_pos(self,delta):
        self.time+=delta
        if self.orbit.e<1:
            if self.time>=self.orbit.T:
                self.time=self.time%self.orbit.T
        self.pos=self.orbit.get_pos_time(self.time)
        for s in self.satellites:
            s.update_pos(delta)

    def add_satellite(self,s):
        self.satellites.append(s)

class Sun(Body):
    def __init__(self, name="", mass=0, pos=None, radius=0):
        Body.__init__(self,primary=None,name=name,mass=mass,pos=pos)
        self.radius=radius
        self.orbit=None
        self.pos=Pos(0,0)

    @property
    def area(self):
        left = self.pos.x - self.radius
        top = self.pos.y + self.radius
        width = self.radius * 2
        height = width
        R = Rectangle(left, top, width, height)
        return R

    def add_planet(self, planet):
        self.add_satellite(planet)

    def soi_body(self,pos):
        body=None
        # finds if pos is under the SOI of a planet
        for b in self.satellites:
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
            body=self
        return body

class Planet(Body):
    def __init__(self, primary=None, name="", mass=0, radius=0,peri=0,apo=0,incl=0,init_pos=0):
        Body.__init__(self,primary=primary,name=name,mass=mass)
        self.radius=radius
        self.orbit=Orbit(name=self.name,focus=primary,peri=peri,apo=apo,incl=incl,mu=G*primary.mass)
        self.mu=G*self.primary.mass
        #self.T = 0  # Orbital period
        # these two should probably be updated always together
        self.pos=self.orbit.pos_true_anomaly_ellipse(init_pos)
        self.time=self.orbit.time_true_anomaly_ellipse(init_pos)
        #(self.pos,self.time)=self.orbit.pos_at_angle(init_pos)
        self.SOI=self.orbit.orbital_path.a*((self.mass/primary.mass)**(2/5))

    def __str__(self):
        t=self.name+" mass:"+"{:.2e}".format(self.mass)+" radius: "+"{:.2e}".format(self.radius)+"\n"
        t+="time: "+str(self.time)+" pos: "+str(self.pos)+"\n"
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
    # parameter sets:
    #   apo,peri,focus, incl=0, name="" has to be a ellipse (apo has not a defined value for hyperbola)
    #   a,e,focus, incl=0, name=""
    # focus is the body at the focus1 of the orbital path
    # incl is the inclination of the orbit
    # mu is G*Mass_of_parent_body
    def __init__(self, **kwargs):

        if 'name' in kwargs:
            self.name=kwargs['name']
        else:
            self.name=""

        if 'incl' in kwargs:
            incl=kwargs['incl']
        else:
            incl=0

        if 'mu' in kwargs:
            self.mu=kwargs['mu']
        else:
            raise SyntaxError("Missing mu in Orbit")

        if all(k in kwargs for k in ("apo","peri","focus")):
            peri=kwargs['peri']
            apo=kwargs['apo']
            focus=kwargs["focus"]
            if (peri > apo):
                (peri, apo) = (apo, peri)
            self.peri = peri
            self.apo = apo

            # a: semi-major axis
            # b: semi-minor axis
            # c: distance from center to focus
            a = (self.peri + self.apo) / 2
            c = a - self.peri
            b = int(math.sqrt((a ** 2) - (c ** 2)))

            # eccentricity
            e = math.sqrt(1 - ((b ** 2) / (a ** 2)))
            if e < 1:
                self.orbital_path = Ellipse(a, e, focus1=focus.pos, incl=incl)
                self.T = (2 * math.pi) * math.sqrt(self.orbital_path.a ** 3 / (G * focus.mass))
            else:
                raise ValueError("eccentricity >=1 in elliptical orbit")

            pass
        elif all(k in kwargs for k in ("a","e","focus")):
            a=kwargs['a']
            e = kwargs['e']
            focus = kwargs['focus']
            if e<1:
                #ellipse
                self.orbital_path = Ellipse(a, e, focus1=focus.pos, incl=incl)
                self.T = (2 * math.pi) * math.sqrt(self.orbital_path.a ** 3 / (G*focus.mass))
            else:
                #hyperbola
                self.orbital_path = Hyperbola(a, e, focus1=focus.pos, incl=incl)

        else:
            raise SyntaxError("arguments in Orbit")

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
        t="a:"+"{:.2e}".format(self.orbital_path.a)+", "+"b:"+"{:.2e}".format(self.orbital_path.b)+"\n"
        r=self.area
        t+="top:"+"{:.2e}".format(r.top)+", left:"+"{:.2e}".format(r.left)+", bottom:"+"{:.2e}".format(r.bottom)+", right:"+"{:.2e}".format(r.right)+"\n"
        return t

    @property
    def a(self):
        return self.orbital_path.a

    @property
    def b(self):
        return self.orbital_path.b

    @property
    def e(self):
        return self.orbital_path.e



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

    # En in radians
    def Newton_Ellipse(self,M,En):
        cos=math.cos(En)
        sin=math.sin(En)
        e=self.orbital_path.e
        a=En-((En-(e*sin)-M)/(1-(e*cos)))
        return a

    def Newton_Hyperbola(self,M,En):
        cos=math.cosh(En)
        sin=math.sinh(En)
        e=self.orbital_path.e
        a=En-(((e*sin)-En-M)/((e*cos)-1))
        return a

    # gets pos in the orbit, t seconds after passing the periapsis
    def get_pos_time(self,t):
        e = self.orbital_path.e
        if e<1:
            # Mean anomaly in radians
            M=(2*math.pi/self.T)*t
            # Solve Kepler using Newton-Raphson
            E=M
            delta=1
            cont=0
            while(delta > NEWTON_THRESHOLD):
                Enew=self.Newton_Ellipse(M,E)
                delta=abs(Enew-E)
                E=Enew
                cont+=1
            print ("Iterations: "+str(cont))
            # E is the eccentric anomaly in radians
            # Calculate the true anomaly using the relation between the tan of the half true anomaly
            # and the eccentric anomaly

            temp=math.sqrt((1+e)/(1-e))*math.tan(E/2)
            v=2*math.atan(temp)
            pos=self.pos_true_anomaly_ellipse(v)
            return pos
        else: # e>1
            #todo OjO e==1
            M=math.sqrt(self.mu/(self.orbital_path.a**3))*t
            E=M
            delta=1
            cont=0
            while(delta > NEWTON_THRESHOLD):
                Enew=self.Newton_Hyperbola(M,E)
                delta=abs(Enew-E)
                E=Enew
                cont+=1
            print ("Iterations: "+str(cont))
            tanh=math.tanh(E/2)
            denom=math.sqrt((e-1)/(e+1))
            v=2*math.atan(tanh/denom)
            # determine pos in elliptical orbit from true anomaly
            pos=self.pos_true_anomaly_hyperbola(v)
            return pos


    def pos_true_anomaly_ellipse(self,alfa):
        # alfa is the true anomaly in radians. 0  is at periapsis
        # orbit.incl is the theta
        sinalfa = math.sin(alfa)
        cosalfa = math.cos(alfa)
        a = self.orbital_path.a
        b = self.orbital_path.b
        e = self.orbital_path.e
        sintheta = self._sintheta
        costheta = self._costheta

        # this is wrong, should only work for circular orbits (a=b)
        # however it gives a good aprox when the position is calculated from the center
        # (shifted from the center after calculating x and y
        #x = int((a * cosalfa * costheta) - (b * sinalfa * sintheta))
        #y = int((a * cosalfa * sintheta) + (b * sinalfa * costheta))

        semilatus=self.orbital_path.l
        r=semilatus/(1+(e*cosalfa))

        x = int((r * cosalfa * costheta) - (r * sinalfa * sintheta))
        y = int((r * cosalfa * sintheta) + (r * sinalfa * costheta))


        Q = Pos(x, y)
        pos = Q + self.focus
        #pos = Q + self.orbital_path.center
        return pos

    def pos_true_anomaly_hyperbola(self,alfa):
        # alfa is the true anomaly in radians. 0  is at periapsis
        # orbit.incl is the theta
        sinalfa = math.sin(alfa)
        cosalfa = math.cos(alfa)
        a = self.orbital_path.c-self.orbital_path.a
        b = self.orbital_path.b
        sintheta = self._sintheta
        costheta = self._costheta
        e=self.orbital_path.e

        semilatus=self.orbital_path.l
        r=semilatus/(1+(e*cosalfa))

        x=r*cosalfa
        y=r*sinalfa

        rot_x = int((x * costheta) - (y * sintheta))
        rot_y = int((x * sintheta) + (y * costheta))

        Q = Pos(rot_x, rot_y)
        pos = Q + self.focus
        return pos


    # gets the time after periapsis corresponding to the true anomaly
    def time_true_anomaly_ellipse(self,v):
        e=self.orbital_path.e
        num=math.tan(v/2)
        denom=math.sqrt((1+e)/(1-e))
        tan12E=num/denom
        E=2*math.atan(tan12E)
        M=E-(e*math.sin(E))
        t=(M*self.T)/(2*math.pi)
        return t


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

    # Calculates the primary body of the ship (according to its position)
    # and adds it to the list of ships in the solar system
    def add_ship(self,ship):
        pos=ship.pos
        prim = self.Sol.soi_body(pos)
        ship.primary=prim
        self.ships.append(ship)

    def update(self,delta):
        self.epoch+=delta
        if(self.epoch/86400>self.days):
            self.days+=1

        for p in self.Sol.satellites:
            p.update_pos(delta)

        for s in self.ships:
            s.update_pos(delta)
            p=s.pos
            prim = self.Sol.soi_body(p)
            if prim != s.primary:
                s.primary = prim



    # updates delta seconds
    # def update(self,delta):
    #     self.epoch+=delta
    #     if(self.epoch/86400>self.days):
    #         self.days+=1
    #
    #     # Planets and satellites go on rails, we can forecast
    #     for p in self.Sol.satellites:
    #         p.update_pos(delta)
    #
    #     # updates the SOI of ships
    #     for s in self.ships:
    #         p=s.pos
    #         prim = self.Sol.soi_body(p)
    #         if prim != s.primary:
    #             s.primary = prim
    #
    #     # if the delta is to big, we are more granular on the ship updates
    #     # parameters here are:
    #     #   threshold for the ship calculation
    #     #   delta for the ship updates
    #     if delta>=600
    #         cont=0
    #         while cont<=delta:
    #             for s in self.ships:
    #                 s.update_pos(10)
    #             cont+=10
    #     else:
    #         for s in self.ships:
    #             #print("Updating ship"+s.name)
    #             s.update_pos(delta)
    #             #print(s.pos)

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
            #print("project "+str(cont))
        self.projecting = False

    def project_ships(self):
        for s in self.ships:
            s.project()


class Ship(Body):
    def __init__(self,name="",mass=0,pos=Pos(0,0),vel=None):
        #Initially there is no primary body
        prim=None
        Body.__init__(self, prim, name=name, mass=mass)

        self.pos=pos
        if vel==None:
            self.velocity=Vector(pos=Pos(0,0))
        else:
            self.velocity=vel

        self.orbit=None
        self.path=[]

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

    # every time that the primary body is updated, the orbit parameters are re-calculated
    @Body.primary.setter
    def primary(self,p):
        Body.primary.fset(self,p)
        self.update_orbit()

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

    def update_orbit(self):
        if self.primary:
            (a, b, ecc, peri, apo, incl)=self.orbital_params()
            self.orbit=Orbit(a=a,e=ecc,focus=self.primary,mu=G*self.primary.mass,incl=incl)

    def orbital_params(self):
        return self.orbital_params_new()

    def orbital_params_new(self):
        m=self.mass
        # p momentum vector
        p=m*self.velocity
        # L angular momentum vector
        r=Vector(start=self.primary.pos,end=self.pos)
        L=r.cross_product(p)

        k=m*self.primary.mass*G

        # runit vector
        dir=r.direction
        runit=Vector(magnitud=1,dir=dir)

        pL=p.cross_product(L)
        mkr=(m*k)*runit

        A=pL-mkr

        Ascaled=A/(m*k)
        ecc=Ascaled.magnitude

        horizontal=Vector(pos=Pos(1,0))
        incl=A.angle(horizontal)


        # semi-major axis
        # a = ( j * j ) / (G * m * | 1 - ecc^2 | )
        j=r.cross_product(self.velocity)
        jj=j.dot_product(j)
        factor = abs(1 - (ecc ** 2))
        denom=G*self.primary.mass*factor
        a=jj/denom
        b=a*math.sqrt(factor)
        #print("b: "+str(b))

        # c: distance from center to focus
        c=a*ecc
        peri=a-c
        apo=a+c

        return(a,b,ecc,peri,apo,incl)




    # From: https://github.com/cmaureir/python-kepler/blob/master/KeplerianOrbit.py
    # returns tupla with (all distance units in meters):
    # a: semi-major axis
    # b: semi-minor axis
    # ecc: eccentricity
    # peri: value of periapsis
    # apo: value of apoapsis
    # incl: orbit inclination (degrees)
    def orbital_params_old(self):
        mu=self.primary.mass*G

        # angular momentum
        # j = r x v
        # OjO pos should be calculated from the focus. In my examples, the focus is at 0,0 but
        # that will not happen always
        # probably need to rewrite the vector class
        posVector=Vector(pos=self.pos)
        jv=posVector.cross_product(self.velocity)
        # Runge-Lenz vector
        # e = { (v x j) / (G * m) }  - { r / |r| }
        tv=self.velocity.cross_product(jv)
        tv=tv/mu
        rv=Vector(pos=self.pos)
        rmag=rv.magnitude
        vv=rv/rmag
        ev=tv-vv

        # ev points (I believe) in the direction of the symmetry axis of the ellipse
        horizontal=Vector(pos=Pos(1,0))
        incl=ev.angle(horizontal)
        #print("incl:",incl)

        # Eccentricity
        ecc=ev.magnitude
        #print("ecc: "+str(ecc))
        # semi-major axis
        # a = ( j * j ) / (G * m * | 1 - ecc^2 | )
        k=jv.dot_product(jv)
        factor=abs(1-(ecc**2))
        a=k/(mu*factor)
        #print("a: "+str(a))

        # semi-minor axis
        b=a*math.sqrt(factor)
        #print("b: "+str(b))

        # c: distance from center to focus
        c=a*ecc
        peri=a-c
        apo=a+c

        return(a,b,ecc,peri,apo,incl)

# # A body that is not on rails
# class Ship:
#     def __init__(self,primary=None,name="",mass=0,pos=Pos(0,0),vel=None):
#         self.primary=primary
#         self.name=name
#         self.mass=mass
#         self.pos=pos
#         if vel==None:
#             self.velocity=Vector(pos=Pos(0,0))
#         else:
#             self.velocity=vel
#
#         # Projection
#         self.path=[]
#         self.orbit=None
#
#     def __str__(self):
#         t=self.name+" ("+str(self.mass)+"Kg)\n"
#         t+="Primary: "+self.primary.name+"\n"
#         t+="Pos: "+str(self.pos)+"\n"
#         t+="Vel: "+str(self.velocity)
#         return t
#
#     def __copy__(self):
#         cls = self.__class__
#         result = cls.__new__(cls)
#         result.__dict__.update(self.__dict__)
#         return result
#
#     def __deepcopy__(self, memo={}):
#         cls = self.__class__
#         result = cls.__new__(cls)
#         memo[id(self)] = result
#         for k, v in self.__dict__.items():
#             setattr(result, k, deepcopy(v, memo))
#         return result
#
#     def update_pos(self,delta):
#         # Calculates the magnitud of the gravitational force
#         f=self.Fg()
#         # the vector has origin in the ship and points to the center of the primary
#         # all our vectors have origin at (0,0) so we calculate de vector at (0,0) that
#         # has the right magnitude and direction
#         pos=self.primary.pos-self.pos
#         vector=Vector(pos=pos)
#         vector.magnitude=f
#         self.velocity+=vector
#         shift=Pos(self.velocity.x*delta,self.velocity.y*delta)
#         self.pos+=shift
#         newpos=deepcopy(self.pos)
#         self.path.append(newpos)
#         #print(self.velocity)
#         self.project()
#
#     def Fg(self):
#         d=self.pos.distance(self.primary.pos)
#         f=G*(self.primary.mass/(d**2))
#         return f
#
#     @property
#     def area(self):
#         # todo: by now all ships have 10x10m
#         side=10
#         left = self.pos.x - side
#         top = self.pos.y + side
#         width = side
#         height = width
#         R = Rectangle(left, top, width, height)
#         return R
#
#     # From: https://github.com/cmaureir/python-kepler/blob/master/KeplerianOrbit.py
#     # returns tupla with (all distance units in meters):
#     # a: semi-major axis
#     # b: semi-minor axis
#     # ecc: eccentricity
#     # peri: value of periapsis
#     # apo: value of apoapsis
#     # incl: orbit inclination (degrees)
#     def orbital_params(self):
#         mu=self.primary.mass*G
#
#         # angular momentum
#         # j = r x v
#         posVector=Vector(pos=self.pos)
#         jv=posVector.cross_product(self.velocity)
#         # Rung-Lez vector
#         # e = { (v x j) / (G * m) }  - { r / |r| }
#         tv=self.velocity.cross_product(jv)
#         tv=tv/mu
#         rv=Vector(pos=self.pos)
#         rmag=rv.magnitude
#         vv=rv/rmag
#         ev=tv-vv
#
#         # ev points (I believe) in the direction of the symmetry axis of the ellipse
#         horizontal=Vector(pos=Pos(1,0))
#         incl=ev.angle(horizontal)
#         #print("incl:",incl)
#
#         # Eccentricity
#         ecc=ev.magnitude
#         #print("ecc: "+str(ecc))
#         # semi-major axis
#         # a = ( j * j ) / (G * m * | 1 - ecc^2 | )
#         k=jv.dot_product(jv)
#         factor=abs(1-(ecc**2))
#         a=k/(mu*factor)
#         #print("a: "+str(a))
#
#         # semi-minor axis
#         b=a*math.sqrt(factor)
#         #print("b: "+str(b))
#
#         # c: distance from center to focus
#         c=a*ecc
#         peri=a-c
#         apo=a+c
#
#         return(a,b,ecc,peri,apo,incl)
#
#     def project(self):
#         (a, b, e, peri, apo, incl) = self.orbital_params()
#         o = Orbit(focus=self.primary, a=a, e=e, incl=incl)
#         self.orbit = o









