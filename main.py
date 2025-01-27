import pygame
import sys
import math

pygame.init()

# -------------------------------------------------
# 1. WINDOW / LAYOUT CONSTANTS
# -------------------------------------------------
SIM_WIDTH = 1280       # Width of the simulation area
SIM_HEIGHT = 1024      # Height of the simulation area
UI_HEIGHT = 400        # Enough space for the entire periodic table layout
WINDOW_HEIGHT = SIM_HEIGHT + UI_HEIGHT

screen = pygame.display.set_mode((SIM_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Physics with a More Accurate Periodic Table")
clock = pygame.time.Clock()
FPS = 60

# -------------------------------------------------
# 2. PHYSICS CONSTANTS
# -------------------------------------------------
GRAVITY = 9.80665
AIR_DENSITY = 0.001225      # g/cm^3 (scaled 2D approximation)
DRAG_COEFFICIENT = 0.5
PIXELS_PER_METER = 1.0
MASS_SCALE = 100000

# -------------------------------------------------
# 3. CORE PHYSICS FUNCTIONS
# -------------------------------------------------
def compute_mass(density, radius):
    """Compute a 2D 'mass' from density and circle area (pi*r^2)."""
    area = math.pi * (radius ** 2)
    return density * area * MASS_SCALE


# -------------------------------------------------
# 4. FULL (or close to full) PERIODIC TABLE DATA
# -------------------------------------------------
PERIODIC_TABLE_INFO = {
    1:  {"symbol": "H",  "name": "Hydrogen",  "row": 1, "col": 1,  "density": 0.00008988,  "color": (255, 0, 0)},
    2:  {"symbol": "He", "name": "Helium",    "row": 1, "col": 18, "density": 0.0001785,   "color": (0, 255, 255)},
    3:  {"symbol": "Li", "name": "Lithium",   "row": 2, "col": 1,  "density": 0.534,       "color": (200, 200, 100)},
    4:  {"symbol": "Be", "name": "Beryllium", "row": 2, "col": 2,  "density": 1.85,        "color": (180, 180, 100)},
    5:  {"symbol": "B",  "name": "Boron",     "row": 2, "col": 13, "density": 2.37,        "color": (128, 255, 128)},
    6:  {"symbol": "C",  "name": "Carbon",    "row": 2, "col": 14, "density": 2.267,       "color": (80, 80, 80)},
    7:  {"symbol": "N",  "name": "Nitrogen",  "row": 2, "col": 15, "density": 0.0012506,   "color": (128, 128, 255)},
    8:  {"symbol": "O",  "name": "Oxygen",    "row": 2, "col": 16, "density": 0.001429,    "color": (255, 100, 100)},
    9:  {"symbol": "F",  "name": "Fluorine",  "row": 2, "col": 17, "density": 0.001696,    "color": (200, 255, 200)},
    10: {"symbol": "Ne", "name": "Neon",      "row": 2, "col": 18, "density": 0.0008999,   "color": (128, 255, 255)},
    11: {"symbol": "Na", "name": "Sodium",    "row": 3, "col": 1,  "density": 0.97,        "color": (200, 200, 150)},
    12: {"symbol": "Mg", "name": "Magnesium", "row": 3, "col": 2,  "density": 1.738,       "color": (150, 150, 150)},
    # ... fill in more real data as desired ...
}

# Insert placeholders for atomic numbers 13..118
placeholder_colors = (100, 100, 100)  # gray
for z in range(13, 119):
    if z not in PERIODIC_TABLE_INFO:
        # A naive approach to guess row, col:
        if   z <= 18:   r, c = 3, (z - 12)
        elif z <= 36:   r, c = 4, (z - 18)
        elif z <= 54:   r, c = 5, (z - 36)
        elif z <= 86:   r, c = 6, (z - 54)
        elif z <= 118:  r, c = 7, (z - 86)

        PERIODIC_TABLE_INFO[z] = {
            "symbol": f"El{z}",
            "name": f"Element {z}",
            "row": r,
            "col": c,
            "density": 1.0,  # placeholder
            "color": placeholder_colors
        }

DEFAULT_RADIUS = 8
for z, data in PERIODIC_TABLE_INFO.items():
    if "radius" not in data:
        data["radius"] = DEFAULT_RADIUS

# -------------------------------------------------
# 5. BUILD UI-PLACEMENT FOR EACH ELEMENT
# -------------------------------------------------
CELL_SIZE = 40
CELL_MARGIN = 2
TABLE_CELLS = {}

def init_periodic_table_ui():
    total_cols = 18
    table_width = total_cols * CELL_SIZE
    x_offset = (SIM_WIDTH - table_width) // 2
    y_offset = SIM_HEIGHT  # start at top of UI panel

    for z, data in PERIODIC_TABLE_INFO.items():
        row = data["row"]
        col = data["col"]
        cell_x = x_offset + (col - 1) * CELL_SIZE
        cell_y = y_offset + (row - 1) * CELL_SIZE
        rect = pygame.Rect(cell_x, cell_y, CELL_SIZE - CELL_MARGIN, CELL_SIZE - CELL_MARGIN)

        TABLE_CELLS[z] = {
            "symbol": data["symbol"],
            "name": data["name"],
            "density": data["density"],
            "color": data["color"],
            "radius": data["radius"],
            "rect": rect
        }

def draw_periodic_table(surface, selected_atomic_num):
    pygame.draw.rect(surface, (50, 50, 50), (0, SIM_HEIGHT, SIM_WIDTH, UI_HEIGHT))

    font = pygame.font.SysFont(None, 20)
    for z, cell_data in TABLE_CELLS.items():
        r = cell_data["rect"]
        sym = cell_data["symbol"]

        if z == selected_atomic_num:
            pygame.draw.rect(surface, (200, 200, 0), r)
        else:
            pygame.draw.rect(surface, cell_data["color"], r)

        text = font.render(sym, True, (255, 255, 255))
        text_rect = text.get_rect(center=r.center)
        surface.blit(text, text_rect)

# -------------------------------------------------
# 6. PARTICLE CLASS
# -------------------------------------------------
class Particle:
    def __init__(self, x, y, atomic_number):
        info = PERIODIC_TABLE_INFO.get(atomic_number, None)
        if info is None:
            self.symbol = f"El{atomic_number}"
            self.density = 1.0
            self.color = (100, 100, 100)
            self.radius = 8
        else:
            self.symbol = info["symbol"]
            self.density = info["density"]
            self.color = info["color"]
            self.radius = info["radius"]

        area = math.pi * (self.radius ** 2)
        self.mass = self.density * area * MASS_SCALE

        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

    def apply_forces(self, dt):
        F_gravity = self.mass * GRAVITY

        area = math.pi * (self.radius ** 2)
        F_buoy = AIR_DENSITY * area * GRAVITY * MASS_SCALE

        F_net_vertical = F_gravity - F_buoy

        speed_sq = self.vx*self.vx + self.vy*self.vy
        if speed_sq > 0:
            speed = math.sqrt(speed_sq)
            F_drag = 0.5 * AIR_DENSITY * DRAG_COEFFICIENT * area * speed_sq * MASS_SCALE
            drag_dx = -F_drag * (self.vx / speed)
            drag_dy = -F_drag * (self.vy / speed)
        else:
            drag_dx, drag_dy = 0.0, 0.0

        F_net_x = drag_dx
        F_net_y = F_net_vertical + drag_dy

        ax = F_net_x / self.mass
        ay = F_net_y / self.mass

        self.vx += ax * dt
        self.vy += ay * dt

    def update_position(self, dt):
        self.x += self.vx * dt * PIXELS_PER_METER
        self.y += self.vy * dt * PIXELS_PER_METER

        if self.y + self.radius >= SIM_HEIGHT:
            self.y = SIM_HEIGHT - self.radius
            self.vy = -0.5 * self.vy

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -0.5 * self.vy

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -0.5 * self.vx

        if self.x + self.radius > SIM_WIDTH:
            self.x = SIM_WIDTH - self.radius
            self.vx = -0.5 * self.vx

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# -------------------------------------------------
# 7. COLLISION HANDLING WITH NaN SAFEGUARD
# -------------------------------------------------
def resolve_collisions(particles):
    n = len(particles)
    for i in range(n):
        for j in range(i + 1, n):
            p1 = particles[i]
            p2 = particles[j]

            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dist_sq = dx*dx + dy*dy
            min_dist = p1.radius + p2.radius

            if dist_sq < min_dist*min_dist:
                dist = math.sqrt(dist_sq)
                if dist < 1e-12:
                    dist = 1e-12

                overlap = (min_dist - dist)
                nx = dx / dist
                ny = dy / dist

                # Overlap correction
                p1.x -= nx * overlap * 0.5
                p1.y -= ny * overlap * 0.5
                p2.x += nx * overlap * 0.5
                p2.y += ny * overlap * 0.5

                # Elastic collision
                vx_rel = p1.vx - p2.vx
                vy_rel = p1.vy - p2.vy
                dot = vx_rel*nx + vy_rel*ny

                if dot > 0:
                    continue

                m1 = p1.mass
                m2 = p2.mass

                coeff1 = (2.0 * m2 / (m1 + m2)) * dot
                p1.vx -= coeff1 * nx
                p1.vy -= coeff1 * ny

                coeff2 = (2.0 * m1 / (m1 + m2)) * dot
                p2.vx += coeff2 * nx
                p2.vy += coeff2 * ny

# -------------------------------------------------
# 8. MAIN LOOP (With Substepping)
# -------------------------------------------------
def main():
    init_periodic_table_ui()
    current_atomic_num = 1
    particles = []

    # Number of substeps to perform each frame
    NUM_SUBSTEPS = 4

    while True:
        dt = clock.tick(FPS) / 1000.0

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my < SIM_HEIGHT:
                    # Click in simulation area -> spawn particle
                    p = Particle(mx, my, current_atomic_num)
                    particles.append(p)
                else:
                    # Click in UI area -> check which cell
                    for z, cell_data in TABLE_CELLS.items():
                        if cell_data["rect"].collidepoint(mx, my):
                            current_atomic_num = z
                            break

        # PHYSICS SUBSTEPS
        sub_dt = dt / NUM_SUBSTEPS
        for _ in range(NUM_SUBSTEPS):
            # 1) Apply forces
            for p in particles:
                p.apply_forces(sub_dt)

            # 2) Update positions
            for p in particles:
                p.update_position(sub_dt)

            # 3) Resolve collisions
            resolve_collisions(particles)

        # RENDER
        screen.fill((30, 30, 30))

        for p in particles:
            p.draw(screen)

        draw_periodic_table(screen, current_atomic_num)
        pygame.display.flip()

if __name__ == "__main__":
    main()
