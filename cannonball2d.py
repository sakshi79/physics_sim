# Copyright - Sakshi Bhatia, 2026
# Python version of Matthias Müller - Ten Minute Physics

import numpy as np
import pygame

pygame.init()

# canvas setup -------------------------------------------------------

# info = pygame.display.Info()
canvas_width = 800
canvas_height = 800
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Cannonball")

sim_min_width = 20.0
c_scale = min(canvas_width, canvas_height) / sim_min_width
sim_width = canvas_width / c_scale
sim_height = canvas_height / c_scale

def c_x(pos):
    return round(pos[0] * c_scale)

def c_y(pos):
    return round(canvas_height - pos[1] * c_scale)

# scene -------------------------------------------------------

gravity = np.array([0.0, -10.0])
time_step = 1.0 / 60.0

ball = {
    "radius": 0.2,
    "pos": np.array([0.2, 0.2]),
    "vel": np.array([10.0, 15.0]),
}

# drawing -------------------------------------------------------

def draw():
    canvas.fill((255, 255, 255))

    pygame.draw.circle(canvas, (255, 0, 0),
                       (c_x(ball["pos"]), c_y(ball["pos"])),
                       round(c_scale * ball["radius"]))

# simulation ----------------------------------------------------

def simulate():
    ball["vel"] += gravity * time_step
    ball["pos"] += ball["vel"] * time_step

    if ball["pos"][0] < 0.0:
        # collision with left wall, bounce back (same speed, opposite direction)
        ball["pos"][0] = 0.0
        ball["vel"][0] = -ball["vel"][0]
    if ball["pos"][0] > sim_width:
        # collision with right wall
        ball["pos"][0] = sim_width
        ball["vel"][0] = -ball["vel"][0]
    if ball["pos"][1] < 0.0:
        # collision with floor/ground
        ball["pos"][1] = 0.0
        ball["vel"][1] = -ball["vel"][1]

# make pygame call us repeatedly -----------------------------------

def update():
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        simulate()
        draw()
        pygame.display.flip()
        clock.tick(60)

update()

pygame.quit()
