# Copyright - Sakshi Bhatia, 2026
# Python version of Matthias Müller - Ten Minute Physics

import pygame
import numpy as np
import random
import math
import sys
import argparse

pygame.init()
info = pygame.display.Info()
canvas_width  = info.current_w - 20    
canvas_height = info.current_h - 100    
# canvas_width = 1000
# canvas_height = 1000
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Billiard")
font = pygame.font.SysFont("monospace", 16)
sim_min_width = 2.0   # Amount of simulation zoom-in on frame pixels
c_scale = min(canvas_width, canvas_height) / sim_min_width
sim_width = canvas_width / c_scale
sim_height = canvas_height / c_scale

def c_x(pos):
    return round(pos[0] * c_scale)

def c_y(pos):
    return round(canvas_height - pos[1] * c_scale)
    
class Ball:
    def __init__(self, radius, mass, pos, vel):
        self.radius = radius
        self.mass = mass
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
    def simulate(self, gravity, dt):
        self.vel += gravity*dt
        self.pos += self.vel*dt

physics_scene = {
    "gravity":    np.array([0.0, 0.0]),
    "dt" : 1.0 / 60.0, 
    "world_size": np.array([sim_width, sim_height]),
    "paused": True,  # unused for now
    "balls": [],
    "restitution" : 1.0
}

def setup_scene():
    physics_scene["balls"] = []
    num_balls = 20
    for i in range(num_balls):
        radius = 0.05 + random.random()*0.1
        mass = math.pi * radius * radius
        pos = np.array([random.random()*sim_width, random.random()*sim_height])
        vel = np.array([-1.0 + 2.0*random.random(), -1.0 + 2.0*random.random()])  # why: to keep the distribution centered around 0, range: [-1, 1]
        physics_scene["balls"].append(Ball(radius, mass, pos, vel))

def draw():
    canvas.fill((255, 255, 255))
    for ball in physics_scene["balls"]:
        pygame.draw.circle(canvas, (255,0,0), (c_x(ball.pos), c_y(ball.pos)), round(c_scale*ball.radius))
    hud = f"restitution {physics_scene['restitution']:.1f} ↑/↓   R: reset"
    canvas.blit(font.render(hud, True, (40,40,40)), (10,10))


def ball_collision(ball1, ball2, res_coeff):
    del_pos = ball2.pos - ball1.pos
    # Balls can overlap if they move fast enough before the frame detects collision. Happens in our discrete time approach.
    # More advanced simulators implement continuous collision detection (CCD) or time of impact (TOI); computationally expensive 
    d = np.linalg.norm(del_pos)
    if(d==0.0 or d > (ball1.radius + ball2.radius)):
        return
    unit_norm = del_pos * 1.0/d

    # Move each ball back by half the overlap so that they touch again
    corr = (ball1.radius + ball2.radius - d) / 2.0 
    ball1.pos += unit_norm * (-corr)
    ball2.pos += unit_norm * (corr)

    # Take projections of velocity along the axis of collision
    v1 = np.dot(ball1.vel, unit_norm)
    v2 = np.dot(ball2.vel, unit_norm)

    m1 = ball1.mass
    m2 = ball2.mass

    # Only velocity component along the axis of collison is changed by collision, the perpendicular component is unaffected.
    new_v1 = (m1*v1 + m2*v2 - m2*(v1-v2)*res_coeff) / (m1+m2)
    new_v2 = (m1*v1 + m2*v2 - m1*(v2-v1)*res_coeff) / (m1+m2)

    ball1.vel += unit_norm * (new_v1 - v1)
    ball2.vel += unit_norm * (new_v2 - v2)


def wall_collision(ball, world_size):
    if ball.pos[0] < ball.radius:
        # hits left wall
        ball.pos[0] = ball.radius
        ball.vel[0] = -ball.vel[0]
    if ball.pos[0] > world_size[0] - ball.radius:
        # hits right wall
        ball.pos[0] = world_size[0] - ball.radius
        ball.vel[0] = -ball.vel[0]
    if ball.pos[1] < ball.radius:
        # hits floor
        ball.pos[1] = ball.radius
        ball.vel[1] = -ball.vel[1]
    if ball.pos[1] > world_size[1] - ball.radius:
        # hits top wall
        ball.pos[1] = world_size[1] - ball.radius
        ball.vel[1] = -ball.vel[1]
    

def simulate():
    for i in range(len(physics_scene["balls"])):
        ball1 = physics_scene["balls"][i]
        ball1.simulate(physics_scene["gravity"], physics_scene["dt"])

        for j in range(i+1, len(physics_scene["balls"])):
            ball2 = physics_scene["balls"][j]
            ball_collision(ball1, ball2, physics_scene["restitution"])
        wall_collision(ball1, physics_scene["world_size"])

def set_restitution(e):
    physics_scene["restitution"] = round(min(1.0, max(0.0, e)), 1)

def update():
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return     # terminate on ESC
                elif event.key == pygame.K_r:
                    setup_scene()   # reset scene on 'R' key
                elif event.key == pygame.K_UP:
                    set_restitution(physics_scene["restitution"] + 0.1)
                elif event.key == pygame.K_DOWN:
                    set_restitution(physics_scene["restitution"] - 0.1)

        simulate()
        draw()
        pygame.display.flip()
        clock.tick(60)

# setup_scene()
# update()

def restitution_value(text):
    e = float(text)
    if not 0.0 <= e <= 1.0:
        raise argparse.ArgumentTypeError(f"must be between 0.0 and 1.0, got {e}")
    return e

def main():
    parser = argparse.ArgumentParser(description="Billiard - Ten Minute Physics")
    parser.add_argument(
        "--e",
        type=restitution_value,
        default=1.0,
        help="collision elasticity, 0.0 to 1.0 (default: 1.0)"
    )
    args = parser.parse_args()
    physics_scene["restitution"] = args.e

    setup_scene()
    # Once a key is held for 300ms, register it every 50 ms from then (skips only reading the first press if key is held)
    pygame.key.set_repeat(300, 50)   
    update()
    pygame.quit()

if __name__ == "__main__":
    sys.exit(main())


