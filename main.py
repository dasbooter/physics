import pygame
import sys
import math

pygame.init()

# ----------------------------------
# 1. WINDOW AND TIMING
# ----------------------------------
WIDTH, HEIGHT = 1280, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particles with Gravity, Buoyancy, Drag, and Elastic Collisions")

clock = pygame.time.Clock()
FPS = 60

# ----------------------------------
# 2. GLOBAL CONSTANTS
# ----------------------------------

# Gravity (m/s^2)
GRAVITY = 9.80665

# We'll treat 1 pixel = 1 meter (not physically realistic, but simpler for the demo)
PIXELS_PER_METER = 1.0

# Air density in g/cm^3 (approximately 1.225 kg/m^3 => ~0.001225 g/cm^3)
AIR_DENSITY = 0.001225

# Drag coefficient (dimensionless). For a sphere ~0.47. We'll pick ~0.5 for simplicity.
DRAG_COEFFICIENT = 0.5

# A scaling factor to convert our naive "2D mass" from g/cm^3 to something that behaves well
# in the simulation. Adjust as needed.
MASS_SCALE = 100000

# ----------------------------------
# 3. ELEMENTAL DATA
# ----------------------------------
# We keep density in g/cm^3. We define a radius in "pixels".
# Then we convert area => mass, using a 2D approach: mass = density * area * MASS_SCALE
# (In reality, density is 3D, so this is purely illustrative.)

def compute_mass(density, radius):
    """
    Compute a 2D "mass" for the particle:
      area_2D = pi * r^2
      mass = density * area_2D * MASS_SCALE
    """
    area = math.pi * (radius ** 2)
    return density * area * MASS_SCALE

elements = {
    "H": {
        "name": "Hydrogen",
        "symbol": "H",
        "atomic_number": 1,
        "atomic_mass": 1.008,       # g/mol (not used directly here)
        "density": 0.00008988,      # g/cm^3
        "color": (255, 0, 0),       # red
        "radius": 8
    },
    "He": {
        "name": "Helium",
        "symbol": "He",
        "atomic_number": 2,
        "atomic_mass": 4.002602,
        "density": 0.0001785,
        "color": (0, 255, 255),     # cyan
        "radius": 8
    }
}

# Precompute mass for each element
for symbol, data in elements.items():
    data["mass"] = compute_mass(data["density"], data["radius"])

# ----------------------------------
# 4. PARTICLE CLASS
# ----------------------------------
class Particle:
    """
    A 2D circle particle:
      - position (x, y)
      - velocity (vx, vy)
      - radius, mass (from its element data)
      - experiences gravity, buoyancy, drag
      - collides elastically with other particles
    """
    def __init__(self, x, y, element_symbol):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

        self.element_symbol = element_symbol
        data = elements[element_symbol]

        self.color = data["color"]
        self.radius = data["radius"]
        self.mass = data["mass"]  # 2D "mass"
        self.density = data["density"]

    def apply_forces(self, dt):
        """
        Compute net forces: gravity, buoyancy, drag.
        Then update velocity based on F = m * a.
        """
        # 1. Gravity (downward)
        #    F_gravity = mass * g
        F_gravity = self.mass * GRAVITY

        # 2. Buoyancy (upward)
        #    F_buoy = density_of_air * (area_2D) * g
        #    area_2D = pi * r^2
        area = math.pi * (self.radius ** 2)
        F_buoy = AIR_DENSITY * area * GRAVITY * MASS_SCALE  # same scale factor used in mass

        # Net "vertical" force from gravity + buoyancy
        #   If the particle is denser than air, net force is downward (gravity > buoyancy).
        #   If the particle is lighter than air, net force could be upward (buoyancy > gravity).
        F_net_vertical = F_gravity - F_buoy  # (down is +, up is - or vice versa)

        # 3. Drag (opposes velocity)
        #    F_drag = 0.5 * air_density * v^2 * Cd * area
        # We'll treat velocity magnitude in m/s, area_2D in m^2, air_density in g/cm^3 (scaled).
        vx_m = self.vx
        vy_m = self.vy
        speed_sq = vx_m * vx_m + vy_m * vy_m

        if speed_sq > 0:
            speed = math.sqrt(speed_sq)
            # In the same scaled units
            F_drag_magnitude = 0.5 * AIR_DENSITY * DRAG_COEFFICIENT * area * speed_sq * MASS_SCALE

            # Direction opposite velocity
            drag_dx = -F_drag_magnitude * (vx_m / speed)
            drag_dy = -F_drag_magnitude * (vy_m / speed)
        else:
            drag_dx, drag_dy = 0.0, 0.0

        # Combine forces:
        #   Gravity/Buoy is only in vertical dimension (down/up).
        #   Drag can affect both x and y.
        #   => F_net_x = F_drag_x
        #   => F_net_y = (F_gravity - F_buoy) + F_drag_y
        F_net_x = drag_dx
        F_net_y = F_net_vertical + drag_dy

        # Acceleration = F_net / mass
        ax = F_net_x / self.mass
        ay = F_net_y / self.mass

        # Update velocity
        self.vx += ax * dt
        self.vy += ay * dt

    def update_position(self, dt):
        """
        Update the particle's position based on its velocity.
        Constrain within screen bounds.
        """
        self.x += self.vx * dt * PIXELS_PER_METER
        self.y += self.vy * dt * PIXELS_PER_METER

        # Bottom boundary
        if self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy = -0.5 * self.vy  # A little bounce off the floor (dampened)

        # Top boundary (optional, if you don't want them to fly out)
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -0.5 * self.vy

        # Left boundary
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -0.5 * self.vx

        # Right boundary
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -0.5 * self.vx

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


# ----------------------------------
# 5. COLLISION HANDLING
# ----------------------------------
def resolve_collisions(particles):
    """
    Check every pair of particles for overlap. If they collide, perform:
      1) Overlap correction (push them apart)
      2) Elastic collision response (swap velocities along the collision normal
         according to conservation of momentum & kinetic energy).
    """
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
                # They overlap
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.000001

                # 1) Overlap correction (push them so they no longer overlap)
                overlap = min_dist - dist
                # We'll push them half the overlap each, along the normal
                nx = dx / dist
                ny = dy / dist

                p1.x -= nx * overlap * 0.5
                p1.y -= ny * overlap * 0.5
                p2.x += nx * overlap * 0.5
                p2.y += ny * overlap * 0.5

                # 2) Elastic collision response (in 2D, frictionless along the normal)
                #    We'll project velocities along the collision normal and swap them.
                #    Use standard 1D elastic collision formula along the line of centers.
                #    v1' = v1 - (2*m2/(m1+m2)) * [(v1 - v2)•n] n
                #    v2' = v2 - (2*m1/(m1+m2)) * [(v2 - v1)•n] n

                # Relative velocity
                vx_rel = p1.vx - p2.vx
                vy_rel = p1.vy - p2.vy

                # Dot product with normal
                dot = vx_rel * nx + vy_rel * ny

                # If dot > 0, they're moving apart already or tangential, skip
                if dot > 0:
                    continue

                m1 = p1.mass
                m2 = p2.mass
                coeff = (2.0 * m2 / (m1 + m2)) * dot

                # p1's velocity
                p1.vx -= coeff * nx
                p1.vy -= coeff * ny

                # p2's velocity
                coeff = (2.0 * m1 / (m1 + m2)) * dot
                p2.vx += coeff * nx
                p2.vy += coeff * ny


# ----------------------------------
# 6. MAIN GAME LOOP
# ----------------------------------
def main():
    # Choose an element to place when clicking
    current_element_symbol = "H"
    particles = []

    while True:
        dt = clock.tick(FPS) / 1000.0  # seconds per frame

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                p = Particle(mx, my, current_element_symbol)
                particles.append(p)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    current_element_symbol = "H"
                elif event.key == pygame.K_e:
                    current_element_symbol = "He"

        # PHYSICS UPDATES
        # 1) Apply forces (gravity, buoyancy, drag)
        for p in particles:
            p.apply_forces(dt)

        # 2) Update positions
        for p in particles:
            p.update_position(dt)

        # 3) Resolve collisions (no overlap, elastic bounce)
        resolve_collisions(particles)

        # RENDER
        screen.fill((30, 30, 30))
        for p in particles:
            p.draw(screen)

        pygame.display.set_caption(f"Particles (Element: {current_element_symbol})")
        pygame.display.flip()

if __name__ == "__main__":
    main()
