from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rubikscube import *
from solve import solve

from typing import List

app = FastAPI()

origins = [
    "https://cube-solver-frontend.vercel.app"
]

app.add_middleware(CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

color_inpt = List[List[str]]

@app.post("/")
def solve_cube(color_input: color_inpt):
    color_data = parse_color_input(color_input)
    cube_state = build_cube_state(color_data)
    cube = Cube(cube_state)
    sequence = solve(cube)
    return sequence