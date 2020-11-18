from fspace import *
from copy import copy, deepcopy


sol=Body(None,"sol")

p1=Body(sol,"p1")
p2=Body(sol,"p2")
p3=Body(sol,"p3")
sol.satellites=[p1,p2,p3]

otrosol=deepcopy(sol)

sol.satellites[1].name="xxx"

pass