from typing import List, TypedDict

CubeState = TypedDict('CubeState', {'corner_position': list[int],
                                    'corner_orientation': list[int],
                                    'edge_position': list[int],
                                    'edge_orientation': list[int]})

def parse_color_input(color_input: List[List[str]]) -> List[str]:
    output = []
    for i, (ref, cubie) in enumerate(zip(_goal, color_input)):
        if i < 12:
            face1 = ref[0]
            face2 = ref[1]
            
            color1 = cubie[_face_to_axis[face1]]
            color2 = cubie[_face_to_axis[face2]]
            
            final_face1 = _color_to_face[color1]
            final_face2 = _color_to_face[color2]
            
            output.append(final_face1 + final_face2)
        else:
            face1 = ref[0]
            face2 = ref[1]
            face3 = ref[2]
            
            color1 = cubie[_face_to_axis[face1]]
            color2 = cubie[_face_to_axis[face2]]
            color3 = cubie[_face_to_axis[face3]]
            
            final_face1 = _color_to_face[color1]
            final_face2 = _color_to_face[color2]
            final_face3 = _color_to_face[color3]
            
            output.append(final_face1 + final_face2 + final_face3)
    return output
            
def build_cube_state(scramble: List[str]) -> CubeState:
    position = [0] * 20
    orientation = [0] * 20
    
    
    for i, cubie in enumerate(scramble):
        while cubie not in _goal:
            cubie = cubie[1:] + cubie[0]
            orientation[i] += 1
            if orientation[i] == 3:
                raise Exception("Invalid scramble")
        position[i] = _goal.index(cubie) if i < 12 else _goal.index(cubie) - 12
    
    return CubeState({'corner_position': position[12:],
                      'corner_orientation': orientation[12:],
                      'edge_position': position[:12],
                      'edge_orientation': orientation[:12],
                      })

def inverse_move(move: str) -> str:
        return _inverse_move[move]
        
def legal_moves(phase: int) -> list[str]:
    if phase == 2:
        return ["U", "U'", "U2",
                "D", "D'", "D2",
                "F2",
                "B2",
                "L", "L'", "L2",
                "R", "R'", "R2"]
    if phase == 3:
        return ["U", "U'", "U2",
                "D", "D'", "D2",
                "F2",
                "B2",
                "L2",
                "R2"]
    if phase == 4:
        return ["U2",
                "D2",
                "F2",
                "B2",
                "L2",
                "R2"]
    return ["U", "U'", "U2",
             "D", "D'", "D2",
             "F", "F'", "F2",
             "B", "B'", "B2",
             "L", "L'", "L2",
             "R", "R'", "R2"]

class Cube:
    solved_state = CubeState({'corner_position': [0, 1, 2, 3, 4, 5, 6, 7],
                              'corner_orientation': [0, 0, 0, 0, 0, 0, 0, 0],
                              'edge_position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                              'edge_orientation': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})
    
    def __init__(self, init_state: CubeState=solved_state):
        self.corner_position = init_state["corner_position"]
        self.corner_orientation = init_state["corner_orientation"]
        
        self.edge_position = init_state["edge_position"]
        self.edge_orientation = init_state["edge_orientation"]
    
    def __str__(self) -> str:
        return "Corner Position: " + str(self.corner_position) + "\n" + \
               "Corner Orientation: " + str(self.corner_orientation) + "\n" + \
               "Edge Position: " + str(self.edge_position) + "\n" + \
               "Edge Orientation: " + str(self.edge_orientation)
    
    def get_cube_state(self) -> CubeState:
        return CubeState({'corner_position': self.corner_position[:],
                          'corner_orientation': self.corner_orientation[:],
                          'edge_position': self.edge_position[:],
                          'edge_orientation': self.edge_orientation[:]})
    
    # Each cube permutation can be assigned an id depending on the phase
    # The id is not unique for each permutation, but permutations with matching ids are equivalent
    # for the subproblem being solved at the given phase        
    def phase_id(self, phase: int) -> str:
        if phase == 1:
            return str(int("".join([str(edge) for edge in self.edge_orientation]), 2))
        elif phase == 2:
            id = self.corner_orientation.copy()
            # 12 bit binary number with 4 1s that represent the equitorial slice edges
            equitorial_slice_index = int("".join(["1" if edge > 7 else "0" for edge in self.edge_position]), 2) 
            id.append(equitorial_slice_index)
            return " ".join([str(val) for val in id])
        elif phase == 3:
            middle_standing_slice_index = int("".join(["10" if edge > 7 else "00" if edge % 2 == 0 else "01" for edge in self.edge_position]), 2)
            corner_pairing_index = int("".join(["{0:03b}".format(corner & 5) for corner in self.corner_position]), 2)
            corner_parity = False
            for i in range(8):
                for j in range(i + 1, 8):
                    corner_parity ^= self.corner_position[i] > self.corner_position[j]
                    
            return str(middle_standing_slice_index) + " " + str(corner_pairing_index) + " " + str(corner_parity)
        return " ".join([str(x) for x in self.corner_position + self.corner_orientation + self.edge_position + self.edge_orientation])
    
    def turn(self, turn:str):
        next_cube = Cube(self.get_cube_state())
        face, turn = _str_to_turn_tuple[turn]
        
        # Moves the corners and edges of the cube into position
        def turnface(corners, edges, turn):
            if turn == 0:
                next_cube.corner_position[corners[0]] = self.corner_position[corners[1]]
                next_cube.corner_position[corners[1]] = self.corner_position[corners[2]]
                next_cube.corner_position[corners[2]] = self.corner_position[corners[3]]
                next_cube.corner_position[corners[3]] = self.corner_position[corners[0]]
                
                next_cube.corner_orientation[corners[0]] = self.corner_orientation[corners[1]]
                next_cube.corner_orientation[corners[1]] = self.corner_orientation[corners[2]]
                next_cube.corner_orientation[corners[2]] = self.corner_orientation[corners[3]]
                next_cube.corner_orientation[corners[3]] = self.corner_orientation[corners[0]]
                
                next_cube.edge_position[edges[0]] = self.edge_position[edges[1]]
                next_cube.edge_position[edges[1]] = self.edge_position[edges[2]]
                next_cube.edge_position[edges[2]] = self.edge_position[edges[3]]
                next_cube.edge_position[edges[3]] = self.edge_position[edges[0]]
                
                next_cube.edge_orientation[edges[0]] = self.edge_orientation[edges[1]]
                next_cube.edge_orientation[edges[1]] = self.edge_orientation[edges[2]]
                next_cube.edge_orientation[edges[2]] = self.edge_orientation[edges[3]] 
                next_cube.edge_orientation[edges[3]] = self.edge_orientation[edges[0]]
            elif turn == 1:
                next_cube.corner_position[corners[0]] = self.corner_position[corners[3]]
                next_cube.corner_position[corners[3]] = self.corner_position[corners[2]]
                next_cube.corner_position[corners[2]] = self.corner_position[corners[1]]
                next_cube.corner_position[corners[1]] = self.corner_position[corners[0]]
                
                next_cube.corner_orientation[corners[0]] = self.corner_orientation[corners[3]]
                next_cube.corner_orientation[corners[3]] = self.corner_orientation[corners[2]]
                next_cube.corner_orientation[corners[2]] = self.corner_orientation[corners[1]]
                next_cube.corner_orientation[corners[1]] = self.corner_orientation[corners[0]]
                
                next_cube.edge_position[edges[0]] = self.edge_position[edges[3]]
                next_cube.edge_position[edges[3]] = self.edge_position[edges[2]]
                next_cube.edge_position[edges[2]] = self.edge_position[edges[1]]
                next_cube.edge_position[edges[1]] = self.edge_position[edges[0]]
                
                next_cube.edge_orientation[edges[0]] = self.edge_orientation[edges[3]]
                next_cube.edge_orientation[edges[3]] = self.edge_orientation[edges[2]]
                next_cube.edge_orientation[edges[2]] = self.edge_orientation[edges[1]]
                next_cube.edge_orientation[edges[1]] = self.edge_orientation[edges[0]]
            elif turn == 2:
                next_cube.corner_position[corners[0]] = self.corner_position[corners[2]]
                next_cube.corner_position[corners[2]] = self.corner_position[corners[0]]
                next_cube.corner_position[corners[1]] = self.corner_position[corners[3]]
                next_cube.corner_position[corners[3]] = self.corner_position[corners[1]]
                

                next_cube.corner_orientation[corners[0]] = self.corner_orientation[corners[2]]
                next_cube.corner_orientation[corners[2]] = self.corner_orientation[corners[0]]
                next_cube.corner_orientation[corners[1]] = self.corner_orientation[corners[3]]
                next_cube.corner_orientation[corners[3]] = self.corner_orientation[corners[1]]
                

                next_cube.edge_position[edges[0]] = self.edge_position[edges[2]]
                next_cube.edge_position[edges[2]] = self.edge_position[edges[0]]
                next_cube.edge_position[edges[1]] = self.edge_position[edges[3]]
                next_cube.edge_position[edges[3]] = self.edge_position[edges[1]]
                

                next_cube.edge_orientation[edges[0]] = self.edge_orientation[edges[2]]
                next_cube.edge_orientation[edges[2]] = self.edge_orientation[edges[0]]
                next_cube.edge_orientation[edges[1]] = self.edge_orientation[edges[3]]
                next_cube.edge_orientation[edges[3]] = self.edge_orientation[edges[1]]
        def orientedges(edges, turn):
            if turn == 0 or turn == 1:
                next_cube.edge_orientation[edges[0]] = (next_cube.edge_orientation[edges[0]] + 1) % 2
                next_cube.edge_orientation[edges[1]] = (next_cube.edge_orientation[edges[1]] + 1) % 2
                next_cube.edge_orientation[edges[2]] = (next_cube.edge_orientation[edges[2]] + 1) % 2
                next_cube.edge_orientation[edges[3]] = (next_cube.edge_orientation[edges[3]] + 1) % 2
        def orientcorners(corners, turn):
            if turn == 0 or turn == 1:
                next_cube.corner_orientation[corners[0]] = (next_cube.corner_orientation[corners[0]] - 1) % 3
                next_cube.corner_orientation[corners[1]] = (next_cube.corner_orientation[corners[1]] + 1) % 3
                next_cube.corner_orientation[corners[2]] = (next_cube.corner_orientation[corners[2]] - 1) % 3
                next_cube.corner_orientation[corners[3]] = (next_cube.corner_orientation[corners[3]] + 1) % 3
        
        edges, corners = _face_to_idx[face]
        turnface(corners, edges, turn)
        if face == 2 or face == 3: orientedges(edges, turn)
        if face == 2 or face == 3 or face == 4 or face == 5: orientcorners(corners, turn)
        
        return next_cube

_face_to_idx = [([0,  1,  2,  3], [0,  1,  2,  3]),
                ([4,  7,  6,  5], [4,  5,  6,  7]),
                ([0,  9,  4,  8], [0,  3,  5,  4]),
                ([2, 10,  6, 11], [2,  1,  7,  6]),
                ([3, 11,  7,  9], [3,  2,  6,  5]), 
                ([1,  8,  5, 10], [1,  0,  4,  7])]

_inverse_move = {
    "U": "U'",
    "U'": "U",
    "U2": "U2",
    "D": "D'",
    "D'": "D",
    "D2": "D2",
    "F": "F'",
    "F'": "F",
    "F2": "F2",
    "B": "B'",
    "B'": "B",
    "B2": "B2",
    "L": "L'",
    "L'": "L",
    "L2": "L2",
    "R": "R'",
    "R'": "R",
    "R2": "R2"
}

_str_to_turn_tuple = {
    "U": (0, 0),
    "U'": (0, 1),
    "U2": (0, 2),
    "D": (1, 0),
    "D'": (1, 1),
    "D2": (1, 2),
    "F": (2, 0),
    "F'": (2, 1),
    "F2": (2, 2),
    "B": (3, 0),
    "B'": (3, 1),
    "B2": (3, 2),
    "L": (4, 0),
    "L'": (4, 1),
    "L2": (4, 2),
    "R": (5, 0),
    "R'": (5, 1),
    "R2": (5, 2)
}

_color_to_face = {
    "blue": "U", 
    "green": "D",
    "yellow": "F",
    "white": "B",
    "red": "L",
    "orange": "R"
}

_face_to_axis = {
    "U": 1,
    "D": 1,
    "F": 2,
    "B": 2,
    "L": 0,
    "R": 0
}

_goal = [ "UF", "UR", "UB", "UL", 
             "DF", "DR", "DB", "DL", 
             "FR", "FL", "BR", "BL",
		     "UFR", "URB", "UBL", "ULF", 
             "DRF", "DFL", "DLB", "DBR" ]
        
    
    
    