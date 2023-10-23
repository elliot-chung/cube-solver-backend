import random
from rubikscube import *
from solve import solve

def main():
    cube = Cube()
    
    scramble = []
    for _ in range(20):
        move = random.choice(legal_moves(1))
        scramble.append(move)
        cube = cube.turn(move)
    
    print("Scramble:", " ".join(scramble))
    
    print(solve(cube))


if __name__ == '__main__':
    main()