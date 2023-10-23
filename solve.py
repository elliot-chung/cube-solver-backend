from rubikscube import *

# Bidirectional breadth-first search 
# Returns a string of moves that solves the cube
# The cube remains unchanged
def solve(cube: Cube) -> str:
    goal_cube = Cube()
    phase = 0
    
    output = []
    
    while (phase := phase + 1) < 5:
        start_id = cube.phase_id(phase)
        goalId = goal_cube.phase_id(phase)
    
        
        if (start_id == goalId):
            continue
        
        queue = [cube, goal_cube]
        
        visited = {
            start_id : (1, None, None),
            goalId : (2, None, None)
        } # Map of seen ids to (direction, predecessor, last move)
        found = False
        
        while not found:
            old_cube = queue.pop(0)
            old_id = old_cube.phase_id(phase)

            
            for move in legal_moves(phase):
                new_cube = old_cube.turn(move)
                new_id = new_cube.phase_id(phase)
                
                if new_id not in visited:
                    visited[new_id] = (visited[old_id][0], old_id, move)
                    queue.append(new_cube)
                
                elif visited[new_id][0] != visited[old_id][0]:
                    found = True
                    
                    # Realign so the current node is always in the forward direction
                    if visited[old_id][0] == 2:
                        old_id, new_id = new_id, old_id
                        move = inverse_move(move)
                    
                    # Reconstruct the algorithm from the middle out
                    algorithm = [move]
                    
                    # Reconstruct the portion that precedes the current node
                    while old_id != start_id:
                        algorithm.insert(0, visited[old_id][2])
                        old_id = visited[old_id][1]
                        
                    # Reconstruct the portion that follows the current node
                    while new_id != goalId:
                        algorithm.append(inverse_move(visited[new_id][2]))
                        new_id = visited[new_id][1]
                    
                    
                    for move in algorithm:
                        output.append(move)
                        cube = cube.turn(move)
                    
                    break
    return " ".join(output)                    
                        