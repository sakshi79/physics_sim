import pygame
import pymunk
from pymunk import pygame_util
from pymunk import Vec2d
import random
import math
import sys


pygame.init()
info = pygame.display.Info()
canvas_width = info.current_w - 20
canvas_height = info.current_h - 100
screen = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Billiard")
clock = pygame.time.Clock()
draw_options = pygame_util.DrawOptions(screen)

SUBSTEPS = 5
DT = 60.0
SIM_MIN_WIDTH = 2.0
C_SCALE = min(canvas_width, canvas_height) / SIM_MIN_WIDTH
SIM_WIDTH = canvas_width/C_SCALE
SIM_HEIGHT = canvas_height/C_SCALE

draw_options.transform = pymunk.Transform.scaling(C_SCALE)

def add_walls(thickness=0.001):
    corners = [(0,0), (SIM_WIDTH,0), (SIM_WIDTH, SIM_HEIGHT), (0, SIM_HEIGHT)]
    walls = []
    for a,b in zip(corners, corners[1:]+corners[:1]):
        seg = pymunk.Segment(space.static_body, a, b, thickness)
        seg.friction = 0.0
        seg.elasticity = 1.0
        walls.append(seg)
    space.add(*walls)
    return walls

def pre_solve(arbiter, space, data):
    arbiter.restitution = 1.0

space = pymunk.Space()
space.gravity = (0, 0)  # 2d flat table for billiards
space.on_collision(pre_solve=pre_solve)
space.collision_slop = 0.001  # The amount of overlap allowed b/w bodies
# 

def setup_scene():
    balls = []
    num_balls = 20
    for _ in range(num_balls):
        radius = (0.05 + random.random()*0.1) 
        mass = math.pi * radius * radius
        pos = Vec2d(random.random()*SIM_WIDTH, random.random()*SIM_HEIGHT)
        vel = Vec2d((-1.0 + 2.0*random.random()), (-1.0 + 2.0*random.random())) 
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
        body = pymunk.Body(mass, inertia)
        body.position = pos
        body.velocity = vel
        shape = pymunk.Circle(body, radius, Vec2d(0,0))
        space.add(body, shape)
        balls.append(shape)


def main():
    add_walls()
    setup_scene()

    while True:
        for _ in range(SUBSTEPS):
            space.step((1/DT) / SUBSTEPS)

        # Draw pymunk screen
        screen.fill((255,255,255))
        space.debug_draw(draw_options) # Draw physics objects on screen, replace with pygame.draw later for more options to control appearance
        pygame.display.flip()         # Display the updated frame
        clock.tick(DT)                # Cap frame rate to match physics step
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return     # terminate on ESC

    print("done!")

if __name__ == "__main__":
    sys.exit(main())
