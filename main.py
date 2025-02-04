import pygame
import sys
import math

import elements
from elements import PERIODIC_TABLE_ATOMS, COMPOUND_COMMON_NAMES
from particle import Particle
import reactions

pygame.init()

MAIN_WIDTH  = 1000
MAIN_HEIGHT = 500
INFO_WIDTH  = 300
# Increase the UI height to display multiple rows (main table, lanthanides, actinides)
UI_HEIGHT   = 300

WINDOW_WIDTH  = MAIN_WIDTH + INFO_WIDTH
WINDOW_HEIGHT = MAIN_HEIGHT + UI_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Ammonia & More Reactions - Multi-file + Broadphase")
clock = pygame.time.Clock()
FPS = 60

CELL_SIZE = 30

# Global dictionaries for the three UI groups:
TABLE_CELLS_MAIN = {}
TABLE_CELLS_LANTH = {}
TABLE_CELLS_ACT   = {}

selected_particle = None

def build_ui_table():
    global TABLE_CELLS_MAIN, TABLE_CELLS_LANTH, TABLE_CELLS_ACT
    TABLE_CELLS_MAIN = {}
    TABLE_CELLS_LANTH = {}
    TABLE_CELLS_ACT   = {}
    
    # Main table: rows 1 to 7 (full width: 18 columns)
    total_cols = 18
    x_offset_main = (MAIN_WIDTH - total_cols * CELL_SIZE) // 2
    for Z, data in PERIODIC_TABLE_ATOMS.items():
        if data["row"] <= 7:
            row = data["row"]
            col = data["col"]
            cx = x_offset_main + (col - 1) * CELL_SIZE
            cy = MAIN_HEIGHT + (row - 1) * CELL_SIZE
            rect = pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE)
            TABLE_CELLS_MAIN[Z] = {
                "symbol": data["symbol"],
                "mass": data["atomic_mass"],
                "color": data["color"],
                "radius": data["radius"],
                "rect": rect
            }
    # Lanthanides: row 8 – typically 15 elements (columns 3..17).
    lanth_cols = 15
    x_offset_lanth = (MAIN_WIDTH - lanth_cols * CELL_SIZE) // 2
    for Z, data in PERIODIC_TABLE_ATOMS.items():
        if data["row"] == 8:
            # Adjust column: since they originally are in columns 3..17, subtract 2.
            col = data["col"] - 2
            cx = x_offset_lanth + (col - 1) * CELL_SIZE
            cy = MAIN_HEIGHT + 7 * CELL_SIZE  # Immediately below the main table (7 rows)
            rect = pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE)
            TABLE_CELLS_LANTH[Z] = {
                "symbol": data["symbol"],
                "mass": data["atomic_mass"],
                "color": data["color"],
                "radius": data["radius"],
                "rect": rect
            }
    # Actinides: row 9 – same centering as lanthanides.
    for Z, data in PERIODIC_TABLE_ATOMS.items():
        if data["row"] == 9:
            col = data["col"] - 2
            cx = x_offset_lanth + (col - 1) * CELL_SIZE
            cy = MAIN_HEIGHT + 8 * CELL_SIZE  # One row below lanthanides
            rect = pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE)
            TABLE_CELLS_ACT[Z] = {
                "symbol": data["symbol"],
                "mass": data["atomic_mass"],
                "color": data["color"],
                "radius": data["radius"],
                "rect": rect
            }

def draw_periodic_table(surface, selected_z):
    # Draw background for the entire UI table area.
    pygame.draw.rect(surface, (50, 50, 50), (0, MAIN_HEIGHT, MAIN_WIDTH, UI_HEIGHT))
    font = pygame.font.SysFont(None, 16)
    
    # Draw Main Table Cells:
    for Z, cdata in TABLE_CELLS_MAIN.items():
        r = cdata["rect"]
        if Z == selected_z:
            pygame.draw.rect(surface, (200, 200, 0), r)
        else:
            pygame.draw.rect(surface, cdata["color"], r)
        sym = cdata["symbol"]
        txt = font.render(sym, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=r.center)
        surface.blit(txt, txt_rect)
    
    # Draw Lanthanides:
    for Z, cdata in TABLE_CELLS_LANTH.items():
        r = cdata["rect"]
        if Z == selected_z:
            pygame.draw.rect(surface, (200, 200, 0), r)
        else:
            pygame.draw.rect(surface, cdata["color"], r)
        sym = cdata["symbol"]
        txt = font.render(sym, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=r.center)
        surface.blit(txt, txt_rect)
    
    # Draw Actinides:
    for Z, cdata in TABLE_CELLS_ACT.items():
        r = cdata["rect"]
        if Z == selected_z:
            pygame.draw.rect(surface, (200, 200, 0), r)
        else:
            pygame.draw.rect(surface, cdata["color"], r)
        sym = cdata["symbol"]
        txt = font.render(sym, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=r.center)
        surface.blit(txt, txt_rect)

def draw_info_panel(surface, particle):
    panel_rect = pygame.Rect(MAIN_WIDTH, 0, INFO_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(surface, (40, 40, 60), panel_rect)
    if not particle:
        return
    font = pygame.font.SysFont(None, 24)
    lines = []
    sym = particle.symbol or "None"
    cname = elements.COMPOUND_COMMON_NAMES.get(sym, "")
    if cname:
        lines.append(f"Symbol: {sym} ({cname})")
    else:
        lines.append(f"Symbol: {sym}")

    lines.append(f"Mass: {particle.mass:.2f}")
    lines.append(f"Radius: {particle.radius:.1f}")
    sp = math.sqrt(particle.vx ** 2 + particle.vy ** 2)
    lines.append(f"Velocity: ({particle.vx:.2f}, {particle.vy:.2f})")
    lines.append(f"Speed: {sp:.2f}")
    lines.append(f"Pos: ({particle.x:.2f}, {particle.y:.2f})")

    x_start = MAIN_WIDTH + 10
    y_start = 10
    for txt in lines:
        surf = font.render(txt, True, (255, 255, 255))
        surface.blit(surf, (x_start, y_start))
        y_start += 30

def select_particle_right_click(particles, mx, my):
    global selected_particle
    best_p = None
    best_dist_sq = 1e9
    for p in particles:
        if 0 <= p.x <= MAIN_WIDTH and 0 <= p.y <= MAIN_HEIGHT:
            dx = p.x - mx
            dy = p.y - my
            dist_sq = dx * dx + dy * dy
            if dist_sq < p.radius * p.radius and dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_p = p
    selected_particle = best_p

def main():
    elements.build_periodic_table()
    build_ui_table()

    # current_element stores the atomic number of the currently selected element.
    current_element = 1
    particles = []
    NUM_SUBSTEPS = 4

    while True:
        dt = clock.tick(FPS) / 1000.0
        pygame.display.set_caption(f"Multi-file + Broadphase - FPS: {clock.get_fps():.1f}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mx > MAIN_WIDTH:
                    # Click on info panel: do nothing
                    pass
                elif my > MAIN_HEIGHT:
                    # Bottom UI: determine which group was clicked.
                    # Main table area: y in [MAIN_HEIGHT, MAIN_HEIGHT + 7*CELL_SIZE)
                    if MAIN_HEIGHT <= my < MAIN_HEIGHT + 7 * CELL_SIZE:
                        for Z, cdata in TABLE_CELLS_MAIN.items():
                            if cdata["rect"].collidepoint(mx, my):
                                current_element = Z
                                break
                    # Lanthanides: next row
                    elif MAIN_HEIGHT + 7 * CELL_SIZE <= my < MAIN_HEIGHT + 8 * CELL_SIZE:
                        for Z, cdata in TABLE_CELLS_LANTH.items():
                            if cdata["rect"].collidepoint(mx, my):
                                current_element = Z
                                break
                    # Actinides: next row
                    elif MAIN_HEIGHT + 8 * CELL_SIZE <= my < MAIN_HEIGHT + 9 * CELL_SIZE:
                        for Z, cdata in TABLE_CELLS_ACT.items():
                            if cdata["rect"].collidepoint(mx, my):
                                current_element = Z
                                break
                else:
                    if event.button == 1:
                        info = PERIODIC_TABLE_ATOMS[current_element]
                        p = Particle(mx, my, info["atomic_mass"], info["symbol"], info["color"], info["radius"])
                        particles.append(p)
                    elif event.button == 3:
                        select_particle_right_click(particles, mx, my)

        sub_dt = dt / NUM_SUBSTEPS
        for _ in range(NUM_SUBSTEPS):
            for p in particles:
                p.apply_forces(sub_dt)
            for p in particles:
                p.update_position(sub_dt, MAIN_WIDTH, MAIN_HEIGHT)
            # Resolve collisions (which include reactions and elastic bounces)
            reactions.resolve_collisions(particles, MAIN_WIDTH, MAIN_HEIGHT)

        screen.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 20)
        for p in particles:
            p.draw(screen, font=font)
        draw_periodic_table(screen, current_element)
        draw_info_panel(screen, selected_particle)
        pygame.display.flip()

if __name__ == "__main__":
    main()
