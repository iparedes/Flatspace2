from fspace import *
from copy import copy, deepcopy
from geometry import *


# v1=Vector(x=2,y=3,z=4)
# v2=Vector(x=5,y=6,z=7)
# w=v1.cross_product(v2)
# print(w)




sol=Sun("sol",2e30,Pos(0,0),7e8)

ship=Ship(sol,"hop",6e24,Pos(1.5e11,1e7),Vector(x=0,y=3e4))

(peri,apo,incl)=ship.orbital_params()
print(peri,apo,incl)

#
# p1=Body(sol,"p1")
# p2=Body(sol,"p2")
# p3=Body(sol,"p3")
# sol.satellites=[p1,p2,p3]
#
# otrosol=deepcopy(sol)
#
# sol.satellites[1].name="xxx"

# p=Pos(1,2,3)
# q=p/7
# print(q)
# print(q.coordZ())
#
exit()
v1=Vector(x=2,y=0,z=7)

w=v1/2
print(w)
print(w.coordZ())

exit()
v2=Vector(x=2,y=2)

w=v1.cross_product(v2)

print(w)
print(w.coordZ())
z=w/1.7
print(z)
print(z.coordZ())


pass