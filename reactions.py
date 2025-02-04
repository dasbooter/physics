import math
from particle import Particle

# Extra compound data (if not already defined in elements.py)
CO2_DATA = {
    "symbol": "CO₂",
    "mass": 44,  # C (12) + O₂ (32)
    "color": (80, 200, 80),
    "radius": 8
}

NO2_DATA = {
    "symbol": "NO₂",
    "mass": 46,  # N (14) + 2*O (16*2)
    "color": (200, 180, 120),
    "radius": 8
}

CH4_DATA = {
    "symbol": "CH₄",
    "mass": 16,  # C (12) + 4*H (1*4)
    "color": (200, 255, 200),
    "radius": 7
}

# Grid cell size for the spatial broadphase.
CELL_SIZE = 50

def resolve_collisions(particles, main_width, main_height):
    """
    Each frame:
      1) Build broadphase grid and get candidate pairs.
      2) Detect overlapping pairs.
      3) Process reactions (pairwise, triple, quadruple).
      4) Recompute collisions and apply elastic bounce.
    """
    candidate_pairs = build_spatial_grid(particles, main_width, main_height)
    colliding_pairs = detect_overlapping_pairs(particles, candidate_pairs)

    # 1. Pairwise diatomic reactions:
    #    H+H → H₂, N+N → N₂, O+O → O₂, He+He → He₂, Li+Li → Li₂, Be+Be → Be₂,
    #    B+B → B₂, F+F → F₂.
    pairwise_reactions_diatomic(particles, colliding_pairs)

    # 2. Additional pairwise reactions:
    #    - C + O₂ → CO₂
    #    - CO + O  → CO₂
    #    - N + O   → NO
    #    - He + H  → HeH
    #    - Li + H  → LiH
    #    - Be + O  → BeO
    #    - B + F   → BF
    #    - Ne + F  → NeF
    pairwise_reactions_extra(particles, colliding_pairs)

    # 3. Triple collisions:
    #    2H₂ + O₂ → 2H₂O and 2N₂ + O₂ → 2N₂O.
    triple_collision_stoich(particles, colliding_pairs)

    # 4. Quadruple collisions:
    #    N₂ + 3H₂ → 2NH₃.
    quadruple_collision_ammonia(particles, colliding_pairs)

    # Recompute collisions for final elastic bounce.
    candidate_pairs = build_spatial_grid(particles, main_width, main_height)
    colliding_pairs = detect_overlapping_pairs(particles, candidate_pairs)
    do_elastic_bounce(particles, colliding_pairs)

# ------------------------------------------------
# 1. BROADPHASE: BUILD A UNIFORM GRID
# ------------------------------------------------
def build_spatial_grid(particles, main_width, main_height):
    from collections import defaultdict
    grid = defaultdict(list)
    for i, p in enumerate(particles):
        cx = int(p.x // CELL_SIZE)
        cy = int(p.y // CELL_SIZE)
        grid[(cx, cy)].append(i)
    candidate_pairs = []
    neighbors = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1),  (0, 0),  (0, 1),
                 (1, -1),  (1, 0),  (1, 1)]
    for (cx, cy), idx_list in grid.items():
        for dx, dy in neighbors:
            ncx, ncy = cx + dx, cy + dy
            if (ncx, ncy) not in grid:
                continue
            for i1 in idx_list:
                for i2 in grid[(ncx, ncy)]:
                    if i1 < i2:
                        candidate_pairs.append((i1, i2))
    return candidate_pairs

# ------------------------------------------------
# 2. DETECT OVERLAPPING PAIRS (NO BOUNCE)
# ------------------------------------------------
def detect_overlapping_pairs(particles, candidate_pairs):
    colliding_pairs = set()
    for (i1, i2) in candidate_pairs:
        p1 = particles[i1]
        p2 = particles[i2]
        if are_colliding(p1, p2):
            colliding_pairs.add((i1, i2))
    return colliding_pairs

def are_colliding(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    dist_sq = dx * dx + dy * dy
    r_sum = a.radius + b.radius
    return dist_sq < r_sum * r_sum

# ------------------------------------------------
# 3. PAIRWISE REACTIONS (DIATOMIC)
# ------------------------------------------------
def pairwise_reactions_diatomic(particles, colliding_pairs):
    from elements import H2_DATA, N2_DATA, O2_DATA, HE2_DATA, LI2_DATA, BE2_DATA, B2_DATA, F2_DATA
    to_remove = set()
    to_add = []
    n = len(particles)
    for i in range(n - 1):
        if i in to_remove:
            continue
        for j in range(i + 1, n):
            if j in to_remove:
                continue
            if (i, j) not in colliding_pairs:
                continue
            p1 = particles[i]
            p2 = particles[j]
            if p1.symbol == "H" and p2.symbol == "H":
                newp = combine_two(p1, p2, H2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
            elif p1.symbol == "N" and p2.symbol == "N":
                newp = combine_two(p1, p2, N2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
            elif p1.symbol == "O" and p2.symbol == "O":
                newp = combine_two(p1, p2, O2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
            elif p1.symbol == "He" and p2.symbol == "He":
                newp = combine_two(p1, p2, HE2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
            elif p1.symbol == "Li" and p2.symbol == "Li":
                newp = combine_two(p1, p2, LI2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
            elif p1.symbol == "Be" and p2.symbol == "Be":
                newp = combine_two(p1, p2, BE2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
            elif p1.symbol == "B" and p2.symbol == "B":
                newp = combine_two(p1, p2, B2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
            elif p1.symbol == "F" and p2.symbol == "F":
                newp = combine_two(p1, p2, F2_DATA)
                to_remove.update([i, j])
                to_add.append(newp)
    for idx in sorted(to_remove, reverse=True):
        del particles[idx]
    particles.extend(to_add)

def combine_two(a, b, data):
    m_sum = a.mass + b.mass
    vx_sum = a.vx * a.mass + b.vx * b.mass
    vy_sum = a.vy * a.mass + b.vy * b.mass
    x_cen = (a.x + b.x) * 0.5
    y_cen = (a.y + b.y) * 0.5
    p = Particle(x_cen, y_cen, m_sum, data["symbol"], data["color"], data["radius"])
    p.vx = vx_sum / m_sum
    p.vy = vy_sum / m_sum
    return p

# ------------------------------------------------
# 4. PAIRWISE REACTIONS EXTRA
# ------------------------------------------------
def pairwise_reactions_extra(particles, colliding_pairs):
    to_remove = set()
    to_add = []
    n = len(particles)
    for i in range(n - 1):
        if i in to_remove:
            continue
        for j in range(i + 1, n):
            if j in to_remove:
                continue
            if (i, j) not in colliding_pairs:
                continue
            p1 = particles[i]
            p2 = particles[j]
            syms = {p1.symbol, p2.symbol}

            # Reaction: C + O₂ → CO₂.
            if syms == {"C", "O₂"}:
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, CO2_DATA["symbol"], CO2_DATA["color"], CO2_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
            # Reaction: CO + O → CO₂.
            elif syms == {"CO", "O"}:
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, CO2_DATA["symbol"], CO2_DATA["color"], CO2_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
            # Reaction: N + O → NO.
            elif syms == {"N", "O"}:
                from elements import COMPOUND_DATA
                NO_DATA = COMPOUND_DATA.get("NO", {"symbol": "NO", "mass": 30, "color": (200,200,100), "radius": 8})
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, NO_DATA["symbol"], NO_DATA["color"], NO_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
            # Reaction: He + H → HeH.
            elif syms == {"He", "H"}:
                from elements import COMPOUND_DATA
                HEH_DATA = COMPOUND_DATA.get("HeH", {"symbol": "HeH", "mass": 5, "color": (230,230,255), "radius": 6})
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, HEH_DATA["symbol"], HEH_DATA["color"], HEH_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
            # Reaction: Li + H → LiH.
            elif syms == {"Li", "H"}:
                from elements import COMPOUND_DATA
                LIH_DATA = COMPOUND_DATA.get("LiH", {"symbol": "LiH", "mass": 8, "color": (240,240,240), "radius": 6})
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, LIH_DATA["symbol"], LIH_DATA["color"], LIH_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
            # Reaction: Be + O → BeO.
            elif syms == {"Be", "O"}:
                from elements import COMPOUND_DATA
                BEO_DATA = COMPOUND_DATA.get("BeO", {"symbol": "BeO", "mass": 25, "color": (100,255,100), "radius": 7})
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, BEO_DATA["symbol"], BEO_DATA["color"], BEO_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
            # Reaction: B + F → BF.
            elif syms == {"B", "F"}:
                from elements import COMPOUND_DATA
                BF_DATA = COMPOUND_DATA.get("BF", {"symbol": "BF", "mass": 30, "color": (255,160,50), "radius": 7})
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, BF_DATA["symbol"], BF_DATA["color"], BF_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
            # Reaction: Ne + F → NeF.
            elif syms == {"Ne", "F"}:
                from elements import COMPOUND_DATA
                NEF_DATA = COMPOUND_DATA.get("NeF", {"symbol": "NeF", "mass": 39, "color": (220,220,255), "radius": 7})
                m_sum = p1.mass + p2.mass
                vx_sum = p1.vx * p1.mass + p2.vx * p2.mass
                vy_sum = p1.vy * p1.mass + p2.vy * p2.mass
                x_cen = (p1.x + p2.x) * 0.5
                y_cen = (p1.y + p2.y) * 0.5
                newp = Particle(x_cen, y_cen, m_sum, NEF_DATA["symbol"], NEF_DATA["color"], NEF_DATA["radius"])
                newp.vx = vx_sum / m_sum
                newp.vy = vy_sum / m_sum
                to_remove.update([i, j])
                to_add.append(newp)
    for idx in sorted(to_remove, reverse=True):
        del particles[idx]
    particles.extend(to_add)

# ------------------------------------------------
# 5. TRIPLE COLLISION (e.g., 2H₂ + O₂ → 2H₂O, 2N₂ + O₂ → 2N₂O)
# ------------------------------------------------
def triple_collision_stoich(particles, colliding_pairs):
    from elements import H2_DATA, O2_DATA, H2O_DATA, N2_DATA, N2O_DATA
    to_remove = set()
    to_add = []
    n = len(particles)
    for i in range(n - 2):
        if i in to_remove:
            continue
        for j in range(i + 1, n - 1):
            if j in to_remove:
                continue
            if (i, j) not in colliding_pairs:
                continue
            for k in range(j + 1, n):
                if k in to_remove:
                    continue
                if ((i, k) in colliding_pairs) and ((j, k) in colliding_pairs):
                    p1 = particles[i]
                    p2 = particles[j]
                    p3 = particles[k]
                    syms = [p1.symbol, p2.symbol, p3.symbol]
                    # 2H₂ + O₂ → 2H₂O.
                    if syms.count("H₂") == 2 and syms.count("O₂") == 1:
                        to_remove.update([i, j, k])
                        new_water = spawn_two_molecules_3(p1, p2, p3, H2O_DATA)
                        to_add.extend(new_water)
                    # 2N₂ + O₂ → 2N₂O.
                    elif syms.count("N₂") == 2 and syms.count("O₂") == 1:
                        to_remove.update([i, j, k])
                        new_n2o = spawn_two_molecules_3(p1, p2, p3, N2O_DATA)
                        to_add.extend(new_n2o)
    for idx in sorted(to_remove, reverse=True):
        del particles[idx]
    particles.extend(to_add)

def spawn_two_molecules_3(a, b, c, data):
    m_sum = a.mass + b.mass + c.mass
    vx_sum = a.vx * a.mass + b.vx * b.mass + c.vx * c.mass
    vy_sum = a.vy * a.mass + b.vy * b.mass + c.vy * c.mass
    x_cen = (a.x + b.x + c.x) / 3
    y_cen = (a.y + b.y + c.y) / 3
    each_mass = m_sum * 0.5
    vx = vx_sum / m_sum
    vy = vy_sum / m_sum
    pA = Particle(x_cen - 5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pB = Particle(x_cen + 5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pA.vx = vx
    pA.vy = vy
    pB.vx = vx
    pB.vy = vy
    return [pA, pB]

# ------------------------------------------------
# 6. QUAD COLLISION (e.g., N₂ + 3H₂ → 2NH₃)
# ------------------------------------------------
def quadruple_collision_ammonia(particles, colliding_pairs):
    from elements import NH3_DATA
    to_remove = set()
    to_add = []
    n = len(particles)
    for i in range(n - 3):
        if i in to_remove:
            continue
        for j in range(i + 1, n - 2):
            if j in to_remove:
                continue
            if (i, j) not in colliding_pairs:
                continue
            for k in range(j + 1, n - 1):
                if k in to_remove:
                    continue
                if (i, k) not in colliding_pairs or (j, k) not in colliding_pairs:
                    continue
                for l in range(k + 1, n):
                    if l in to_remove:
                        continue
                    if ((i, l) in colliding_pairs and
                        (j, l) in colliding_pairs and
                        (k, l) in colliding_pairs):
                        p1 = particles[i]
                        p2 = particles[j]
                        p3 = particles[k]
                        p4 = particles[l]
                        syms = [p1.symbol, p2.symbol, p3.symbol, p4.symbol]
                        if syms.count("N₂") == 1 and syms.count("H₂") == 3:
                            to_remove.update([i, j, k, l])
                            new_nh3 = spawn_two_molecules_4(p1, p2, p3, p4, NH3_DATA)
                            to_add.extend(new_nh3)
    for idx in sorted(to_remove, reverse=True):
        del particles[idx]
    particles.extend(to_add)

def spawn_two_molecules_4(a, b, c, d, data):
    m_sum = a.mass + b.mass + c.mass + d.mass
    vx_sum = a.vx * a.mass + b.vx * b.mass + c.vx * c.mass + d.vx * d.mass
    vy_sum = a.vy * a.mass + b.vy * b.mass + c.vy * c.mass + d.vy * d.mass
    x_cen = (a.x + b.x + c.x + d.x) / 4
    y_cen = (a.y + b.y + c.y + d.y) / 4
    each_mass = m_sum / 2.0
    vx = vx_sum / m_sum
    vy = vy_sum / m_sum
    pA = Particle(x_cen - 5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pB = Particle(x_cen + 5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pA.vx = vx
    pA.vy = vy
    pB.vx = vx
    pB.vy = vy
    return [pA, pB]

# ------------------------------------------------
# 7. FINAL ELASTIC BOUNCE AFTER REACTIONS
# ------------------------------------------------
def do_elastic_bounce(particles, colliding_pairs):
    for (i1, i2) in colliding_pairs:
        if i1 >= len(particles) or i2 >= len(particles):
            continue
        p1 = particles[i1]
        p2 = particles[i2]
        if p1 is None or p2 is None:
            continue
        if are_colliding(p1, p2):
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dist = math.sqrt(dx * dx + dy * dy) or 1e-12
            overlap = (p1.radius + p2.radius) - dist
            if overlap > 0:
                nx = dx / dist
                ny = dy / dist
                p1.x -= nx * (overlap * 0.5)
                p1.y -= ny * (overlap * 0.5)
                p2.x += nx * (overlap * 0.5)
                p2.y += ny * (overlap * 0.5)
                vx_rel = p1.vx - p2.vx
                vy_rel = p1.vy - p2.vy
                dot = vx_rel * nx + vy_rel * ny
                if dot < 0:
                    m1 = p1.mass
                    m2 = p2.mass
                    c1 = (2 * m2 / (m1 + m2)) * dot
                    p1.vx -= c1 * nx
                    p1.vy -= c1 * ny
                    c2 = (2 * m1 / (m1 + m2)) * dot
                    p2.vx += c2 * nx
                    p2.vy += c2 * ny
