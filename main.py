# main.py
import pygame
import sys
import math

# Our custom modules
import elements
import reactions
from elements import PERIODIC_TABLE_ATOMS, COMPOUND_COMMON_NAMES
from particle import Particle
from particle import MAX_SPEED, MAX_SPEED_SQ, GRAVITY  # if needed

"""
This file:
 - Initializes Pygame
 - Builds the periodic table
 - Main loop with event handling, substepping, collisions, rendering
"""

pygame.init()

# Window layout
MAIN_WIDTH = 1000
MAIN_HEIGHT= 500
INFO_WIDTH = 300
UI_HEIGHT  = 225

WINDOW_WIDTH  = MAIN_WIDTH + INFO_WIDTH
WINDOW_HEIGHT = MAIN_HEIGHT + UI_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Multi-file Chemistry Demo")
clock = pygame.time.Clock()
FPS = 60

# We'll create a dictionary like TABLE_CELLS to store the UI rect for each element
CELL_SIZE = 30
TABLE_CELLS= {}

# For right-click selection
selected_particle = None

def build_ui_table():
    # builds TABLE_CELLS from PERIODIC_TABLE_ATOMS
    total_cols = 18
    x_offset = (MAIN_WIDTH - total_cols*CELL_SIZE)//2
    for Z, data in PERIODIC_TABLE_ATOMS.items():
        row = data["row"]
        col = data["col"]
        cx = x_offset + (col-1)*CELL_SIZE
        cy = MAIN_HEIGHT + (row-1)*CELL_SIZE
        rect= pygame.Rect(cx,cy, CELL_SIZE, CELL_SIZE)
        TABLE_CELLS[Z] = {
            "symbol": data["symbol"],
            "mass": data["atomic_mass"],
            "color": data["color"],
            "radius": data["radius"],
            "rect": rect
        }

def draw_periodic_table(surface, selected_z):
    pygame.draw.rect(surface, (50,50,50), (0, MAIN_HEIGHT, MAIN_WIDTH, UI_HEIGHT))
    font= pygame.font.SysFont(None,16)
    for Z,cdata in TABLE_CELLS.items():
        r = cdata["rect"]
        if Z== selected_z:
            pygame.draw.rect(surface, (200,200,0), r)
        else:
            pygame.draw.rect(surface, cdata["color"], r)
        sym= cdata["symbol"]
        txt= font.render(sym, True, (255,255,255))
        txt_rect= txt.get_rect(center=r.center)
        surface.blit(txt, txt_rect)

def draw_info_panel(surface, particle):
    panel_rect= pygame.Rect(MAIN_WIDTH,0, INFO_WIDTH, MAIN_HEIGHT+UI_HEIGHT)
    pygame.draw.rect(surface, (40,40,60), panel_rect)
    if not particle:
        return
    font= pygame.font.SysFont(None,24)
    lines=[]
    sym= particle.symbol or "None"
    cname= COMPOUND_COMMON_NAMES.get(sym,"")
    if cname:
        lines.append(f"Symbol: {sym} ({cname})")
    else:
        lines.append(f"Symbol: {sym}")

    lines.append(f"Mass: {particle.mass:.2f}")
    lines.append(f"Radius: {particle.radius:.1f}")
    sp= math.sqrt(particle.vx**2 + particle.vy**2)
    lines.append(f"Velocity: ({particle.vx:.2f}, {particle.vy:.2f})")
    lines.append(f"Speed: {sp:.2f}")
    lines.append(f"Pos: ({particle.x:.2f}, {particle.y:.2f})")

    x_start= MAIN_WIDTH+10
    y_start= 10
    for txt in lines:
        surf= font.render(txt, True, (255,255,255))
        surface.blit(surf, (x_start,y_start))
        y_start+=30

def select_particle_rightclick(particles, mx,my):
    global selected_particle
    best_p= None
    best_dist_sq= 1e9
    for p in particles:
        if 0<=p.x<=MAIN_WIDTH and 0<=p.y<=MAIN_HEIGHT:
            dx= p.x - mx
            dy= p.y - my
            dist_sq= dx*dx + dy*dy
            if dist_sq< p.radius*p.radius and dist_sq< best_dist_sq:
                best_dist_sq= dist_sq
                best_p= p
    selected_particle= best_p

def main():
    # build the full dictionary of 118 atoms
    elements.build_periodic_table()
    # build the UI table data
    build_ui_table()

    current_element=1 # default to H
    particles=[]

    NUM_SUBSTEPS=4

    while True:
        dt= clock.tick(FPS)/1000.0
        # show FPS
        pygame.display.set_caption(f"Multi-file Chem - FPS: {clock.get_fps():.1f}")

        # Events
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type== pygame.MOUSEBUTTONDOWN:
                mx,my= pygame.mouse.get_pos()
                # right panel?
                if mx>MAIN_WIDTH:
                    pass
                # bottom UI?
                elif my>MAIN_HEIGHT:
                    # check if user selected an element
                    for Z,cdata in TABLE_CELLS.items():
                        if cdata["rect"].collidepoint(mx,my):
                            current_element= Z
                            break
                else:
                    # in the main sim area
                    if event.button==1:
                        # left-click => spawn
                        info = PERIODIC_TABLE_ATOMS[current_element]
                        p= Particle(mx, my, info["atomic_mass"], info["symbol"], info["color"], info["radius"])
                        particles.append(p)
                    elif event.button==3:
                        # right-click => select
                        select_particle_rightclick(particles,mx,my)

        # Physics steps
        sub_dt= dt/NUM_SUBSTEPS
        for _ in range(NUM_SUBSTEPS):
            for p in particles:
                p.apply_forces(sub_dt)
            for p in particles:
                p.update_position(sub_dt, MAIN_WIDTH, MAIN_HEIGHT)
            reactions.resolve_collisions(particles)

        # Render
        screen.fill((30,30,30))
        # draw particles
        font= pygame.font.SysFont(None,20)
        for p in particles:
            p.draw(screen, font=font)
        # UI
        draw_periodic_table(screen, current_element)
        draw_info_panel(screen, selected_particle)
        pygame.display.flip()

if __name__=="__main__":
    main()
