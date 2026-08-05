# Copyright - Sakshi Bhatia, 2026
# Python version of Matthias Müller - Ten Minute Physics

import sys
import pymunk
import pygame
from pymunk import pygame_util
from pymunk import Vec2d


pygame.init()
info = pygame.display.Info()
canvas_width = info.current_w - 20
canvas_height = info.current_h - 100
canvas = pygame.display.set_mode((canvas_width, canvas_height))
pygame.display.set_caption("Cannonball")
font = pygame.font.SysFont("monospace", 16)
clock = pygame.time.Clock()
draw_options = pygame_util.DrawOptions(canvas)

SIM_MIN_WIDTH = 20.0          # the short side of the window is 20 m across
C_SCALE = min(canvas_width, canvas_height) / SIM_MIN_WIDTH   # pixels per meter
SIM_WIDTH = canvas_width / C_SCALE
SIM_HEIGHT = canvas_height / C_SCALE

DT = 60.0                    # frames (and physics steps) per second
SUBSTEPS = 4

# Physics is in meters, the screen is in pixels: scale at draw time only. 
# See NOTES at file bottom.
draw_options.transform = pymunk.Transform(a=C_SCALE, b=0, c=0, d=-C_SCALE, tx=0, ty=canvas_height)

def add_walls(thickness=0.001):
    edges = [
        ((0, 0),        (SIM_WIDTH, 0)),           # floor
        ((0, 0),        (0, SIM_HEIGHT)),          # left
        ((SIM_WIDTH, 0),(SIM_WIDTH, SIM_HEIGHT)),  # right
    ]    
    walls = []
    for a,b in edges:
        seg = pymunk.Segment(space.static_body, a, b, thickness)
        seg.friction = 0.0
        seg.elasticity = 1.0
        walls.append(seg)
    space.add(*walls)
    return walls

    
####### Initialize Pymunk's physics space #########
space = pymunk.Space()
space.gravity = (0, -10.0)  # gravity: 10 m/s^2       
space.collision_slop = 0.001     # allowed overlap b/w shapes (penetration distance)
# Pymunk doesn't use a CCD, but discrete timestep correction, allowing small overlap to avoid sudden impulse

def setup_scene():
    for s in [s for s in space.shapes if s.body.body_type == pymunk.Body.DYNAMIC]:
        space.remove(s, s.body)  # remove dynamic shapes from space at reset
   
    # cannon ball
    radius = 0.2
    mass = 1.0
    moment_of_inertia = pymunk.moment_for_circle(mass, 0, radius)  # inner radius 0
    ball_body = pymunk.Body(mass, moment_of_inertia)
    ball_body.position = (0.2, 0.2)
    ball_body.velocity = (10.0, 15.0)
    ball_shape = pymunk.Circle(ball_body, radius, Vec2d(0,0))  # The third arg is shape's offset from body's origin (also zero by default)
    # Lossless bounce
    ball_shape.elasticity = 1.0
    ball_shape.friction = 0.0
    space.add(ball_body, ball_shape)
    return ball_shape


def main():
    add_walls()
    ball = setup_scene()
    show_debug = False
    running = True

    while running:
        for _ in range(SUBSTEPS):
            # step simulation (in substeps for stability)
            space.step((1/DT)/SUBSTEPS)

        # Draw Pygame screen
        canvas.fill((255,255,255))
        if show_debug:
            space.debug_draw(draw_options)   # Pymunk's debug draw
        else:
            # Pymunk's cute draw (can control color n stuff)
            p = ball.body.position
            pygame.draw.circle(canvas, (255,0,0), (round(p.x*C_SCALE), round(canvas_height - p.y*C_SCALE)), round(C_SCALE*ball.radius))

        hud = "R: reset    D: debug mode"
        canvas.blit(font.render(hud, True, (40,40,40)), (10,10))
        pygame.display.flip()
        clock.tick(DT)  # Cap frame rate to match physics step


        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # exit cleanly when pygame window's close button is pressed.
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False    # terminate on ESC
                elif event.key == pygame.K_d:
                    # Toggle b/w Pymunk's debug draw mode and pygame's draw
                    show_debug = not show_debug
                elif event.key == pygame.K_r:
                    ball = setup_scene()   # reset scene on 'R' key

    pygame.quit()
    print("done!")


if __name__ == "__main__":
    sys.exit(main())


########## NOTES ############
# pymunk.Transform is a 2-D affine transform — the mapping debug_draw applies to every point before it draws it, to go from physics/world coordinates (meters, y-up) to screen coordinates (pixels, y-down). It's stored as 6 numbers (a, b, c, d, tx, ty) that form this matrix:


#         | a  c  tx |       screen_x = a*x + c*y + tx
#         | b  d  ty |       screen_y = b*x + d*y + ty
#         | 0  0  1  |
# So a world point (x, y) becomes:

# screen_x = a*x + c*y + tx
# screen_y = b*x + d*y + ty
# Plugging in your values a=C_SCALE, b=0, c=0, d=-C_SCALE, tx=0, ty=canvas_height:

# screen_x = C_SCALE * x
# screen_y = canvas_height − C_SCALE * y
