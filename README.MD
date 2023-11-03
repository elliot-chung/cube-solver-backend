# Rubik's Cube Solver Server

The following is python program for solving a rubik's cube. An http server exposes an endpoint that allows a cube configuration to be processed and a sequence of moves will be sent back as a response. The solver uses an implementation of Thistlewaite's algorithm based on [Stefan Pochmann's](https://www.stefan-pochmann.info/spocc/other_stuff/tools/solver_thistlethwaite/solver_thistlethwaite.txt) implementation.

## Cube State

An given rubik's cube configuration can be represented by a 40-dimensional vector. This is because a cube contains 20 "cubies" that can change position (center cubies always stay in the same positions in relation to eachother). The first 20 values are used to track the position of each cubie while the final 20 values are used to track their orientation.

### Position

Notice how every corner cubie can occupy the position of any other corner cubie and how every edge cubie can occupy the same position as any other edge cubie. Because of this 12 values are used to track the position of the edge cubies and 8 values are used to track the value of the corner cubies. Each cubie is assigned an index within the vector and a corresponding id value that mirrors the index. A turn is represented as the 8 values located at the associated indices of the turning face shifting positions.

For convenience, the 20 position values are split and offset such that a solved cube has the following position values:

```
edges: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
corners: [0, 1, 2, 3, 4, 5, 6, 7]
```

Turning a face always rotates 4 indices in each subvector. The result of turning the U face on a solved cube looks like this:

```
edges: [1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11]
corners: [1, 2, 3, 0, 4, 5, 6, 7]
```

### Orientation

Alongside every permutation of position, each cubie can also occupy the same position in multiple orientations. Each corner cubie can be in up to 3 orientations and each edge cubie can be in up to 2. Again, each cubie is assigned to an index in the vector which changes orientation based on which face is turned.

Edge Orientation

One might determine edge orientation by first noticing that any edge cubie that is moved and brought back to its original position in an even number of quarter turns maintains its orientation while a cubie that does the same in an odd number of quarter turns has a flipped orientation. Additionally, moving an edge cubie from one position to another in an even number of quarter turns results in the same ending orientation regardless of the sequence of moves made (the same is true for an odd number of quarter turns). So we could flip the orientation of each associated edge cubie in our orientation vector with each quarter turn but we can simplify even further. Notice how if we exclude the use of any two arbitrary parallel faces, no edge cubie can be moved from its position and returned back in an odd number of moves. This means that if we establish a reference frame by selecting two parallel faces, edge orientation can only be changed by quarter turns on those two faces. This implementation uses the front and back faces for edge orientation.

The following represent the edge positions and orientations of solved cube:

```
edge_position:    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
edge_orientation: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

A rotation of the U face results in positions moving but no change in orientations:

```
edge_position:    [1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11]
edge_orientation: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

A rotation of the F face results in both positions moving and orientations flipping:

```
edge_position:    [9, 1, 2, 3, 8, 5, 6, 7, 0, 4, 10, 11]
edge_orientation: [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0]
```

While the same cubie is in the same position between these two configurations, its orientation is flipped.

<img src="./images/solved.png" width="200">
<img src="./images/flippededge.png" width="213">

Corner Orientation

Determining corner orientation is more complicated given that a corner can occupy a greater number of orientations. To uniquely define each orientation state, notice that by selecting two arbitrary parallel faces, every corner cubie must contain a color from one of the two faces. For example, most Rubik's cubes have the orange and red faces on opposite sides of the cube. Every single corner piece must contain at least one red or one orange side. (Again the choice is arbitrary, so this is also true for the blue/green sides and the yellow/white sides). The side of the cubie that this color occupies directly maps to the three orientations.

The first image shows a correctly oriented corner of orientation 0.

The second image shows a clockwise or +1 rotation resulting in orientation 1.

The third image shows a counter-clockwise -1 rotation resulting in orientation 2 (which is equivalent to -1 under mod 3).

The fourth image depicts an orientation 0 corner because the orange face lies opposite the red face and the orange facet of the critical cubie is aligned with the red face.

<img src="./images/solved.png" width="200">
<img src="./images/cwcorner.png" width="222">
<img src="./images/ccwcorner.png" width="222">
<img src="./images/othercolorcorner.png" width="195">

We can then notice that under these rules, the orientation of a cubie cannot change by turning either the red or orange sides because turns of this face don't change the positional relationship between the critical facet and the selected face. It also works out that turning any other side changes the orientation of 2 diagonal corner cubies by +1 and the other two by -1.

### Parity

In addition to the 40 values required to uniquely define a cube state, this implementation also tracks the parity of the cube. On a 3x3 Rubik's cube, the parity of the cube will equal the number of quarter turns made on cube mod 2. Thus, parity is tracked by a boolean which is flipped each time a quarter turn is made. A more formal definition for parity can be found [here](https://www.sfu.ca/~jtmulhol/math302/notes/302notes-May07-2012.pdf#Permutations%3A+The+Parity+Theorem).

### CubeState Datatype

For convenience, the 40 values that make up the cube state are tracked in four separate arrays. The following is the full cube state of a solved cube:

```
Corner Position: [0, 1, 2, 3, 4, 5, 6, 7]
Corner Orientation: [0, 0, 0, 0, 0, 0, 0, 0]
Edge Position: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
Edge Orientation: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Parity: False
```

And this is the cube state right after making an F turn:

```
Corner Position: [3, 1, 2, 5, 0, 4, 6, 7]
Corner Orientation: [2, 0, 0, 1, 1, 2, 0, 0]
Edge Position: [9, 1, 2, 3, 8, 5, 6, 7, 0, 4, 10, 11]
Edge Orientation: [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0]
Parity: True
```

## [Thistlewaite's Algorithm](https://www.jaapsch.net/puzzles/thistle.htm)

Now that we have a rigorous way of uniquely defining every cube state we can start looking for a solution. Simply put, solution is just a series of face turns that transforms a given scramble cube state into the solved cube state. To do this, cube-solving algorithms tend to represent cube states as the nodes of a graph with each type of turn corresponding to the connections between nodes. Unfortunately, a simple graph search algorithm such as DFS or BFS cannot find a solution a feasible time since a Rubik's cube can occupy 43,252,003,274,489,856,000 unique states and each state branches 18 times. Finding an optimal route through this graph can take many hours even on modern hardware and it still requires pre-computed tables to act as a heuristic for A\* search [(Korf's Algorithm)](https://www.cs.princeton.edu/courses/archive/fall06/cos402/papers/korfrubik.pdf). Thistlewaite's algorithm sacrifices finding the optimal route for much faster calculation speeds. It does this by breaking down the search into sub-problems that search over smaller spaces. It does this by first defining five groups (G<sub>0</sub>, G<sub>1</sub>, G<sub>2</sub>, G<sub>3</sub>, G<sub>4</sub>) that progressively place cubies into their proper orientation then position. Each group is a subgroup of the one that precedes it so the properties of all previous groups apply to any group further down the line.

G<sub>0</sub> - All legal cube states \
G<sub>1</sub> - All cube states with correctly oriented edges \
G<sub>2</sub> - All cube states with correctly oriented corners and the equatorial slice edges positioned within the equitorial slice \
G<sub>3</sub> - All the cube states with the middle and standing slice edge cubies positioned within their respective slices as well as each corner positioned within its respective tetrad (more below)\
G<sub>4</sub> - The solved states
