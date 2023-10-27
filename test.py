import random

from rubikscube import *
from solve import solve

data = [["black","blue","orange"],["white","blue","black"],["black","blue","red"],["yellow","blue","black"],["black","green","yellow"],["orange","green","black"],["black","green","white"],["red","green","black"],["orange","black","yellow"],["red","black","yellow"],["orange","black","white"],["red","black","white"],["white","blue","orange"],["white","blue","red"],["yellow","blue","red"],["yellow","blue","orange"],["orange","green","yellow"],["red","green","yellow"],["red","green","white"],["orange","green","white"]]


cube_state = build_cube_state(parse_color_input(data))

cube = Cube(cube_state)

print(cube)

# for _ in range(100):
#     cube = cube.turn(random.choice(legal_moves(1)))
                     
sequence = solve(cube)

print(sequence)