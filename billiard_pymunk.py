# Copyright - Sakshi Bhatia, 2026
# Python version of Matthias Müller - Ten Minute Physics

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
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Billiard")
font = pygame.font.SysFont("monospace", 16)
clock = pygame.time.Clock()
draw_options = pygame_util.DrawOptions(canvas)

SUBSTEPS = 5
DT = 60.0
SIM_MIN_WIDTH = 2.0
C_SCALE = min(canvas_width, canvas_height) / SIM_MIN_WIDTH
SIM_WIDTH = canvas_width/C_SCALE
SIM_HEIGHT = canvas_height/C_SCALE
res_coeff = 1.0
draw_options.transform = pymunk.Transform(a=C_SCALE, b=0, c=0, d=-C_SCALE, tx=0, ty=canvas_height)

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
    arbiter.restitution = res_coeff

space = pymunk.Space()
space.gravity = (0, 0)  # 2d flat table for billiards
space.on_collision(pre_solve=pre_solve)
space.collision_slop = 0.001  # The amount of overlap allowed b/w bodies
# Pymunk doesn't use a CCD, but discrete timestep correction, allowing small overlap to avoid sudden impulse

def setup_scene():
    for s in [s for s in space.shapes if s.body.body_type == pymunk.Body.DYNAMIC]:
        space.remove(s, s.body)  # remove dynamic shapes from space at reset
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
    return balls

def set_restitution(e):
    global res_coeff
    res_coeff = round(min(1.0, max(0.0, e)), 1)

def main():
    add_walls()
    balls = setup_scene()
    show_debug = False
    running = True

    while running:
        for _ in range(SUBSTEPS):
            space.step((1/DT) / SUBSTEPS)

        # Draw pygame screen
        canvas.fill((255,255,255))
        if show_debug: 
            space.debug_draw(draw_options) 
        else:
            for ball in balls:
                p = ball.body.position
                pygame.draw.circle(canvas, (255,0,0), (round(p.x*C_SCALE), round(canvas_height-p.y*C_SCALE)), round(C_SCALE*ball.radius))

        hud = f"restitution {res_coeff:.1f} ↑/↓    R: reset    D: debug mode"
        canvas.blit(font.render(hud, True, (40,40,40)), (10,10))

        pygame.display.flip()         # Display the updated frame
        clock.tick(DT)                # Cap frame rate to match physics step
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False     # terminate on ESC
                elif event.key == pygame.K_d:
                    # Toggle b/w Pymunk's debug draw mode and pygame's draw
                    show_debug = not show_debug
                elif event.key == pygame.K_r:
                    balls = setup_scene()   # reset scene on 'R' key
                elif event.key == pygame.K_UP:
                    set_restitution(res_coeff + 0.1)
                elif event.key == pygame.K_DOWN:
                    set_restitution(res_coeff - 0.1)

    print("done!")
    pygame.quit()

if __name__ == "__main__":
    sys.exit(main())
