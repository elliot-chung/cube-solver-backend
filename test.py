import random

from rubikscube import *
from solve import solve


cube = Cube()

print(cube)

cube = cube.turn("F")

print(cube)

seq = solve(cube)

print(seq)

