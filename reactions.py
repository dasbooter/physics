# reactions.py
import math
from particle import Particle
from elements import (
    H2_DATA, O2_DATA, N2_DATA,
    H2O_DATA, N2O_DATA, NO_DATA, NH3_DATA
)

CELL_SIZE = 50  # size for our uniform grid

def resolve_collisions(particles, main_width, main_height):
    """
    Each frame:
      1) broadphase => candidate_pairs
      2) detect_overlapping_pairs => colliding_pairs (no bounce yet)
      3) pairwise_reactions_diatomic (H+H => H2, etc.)
      4) triple_collision_stoich (2H2+O2 =>2H2O, etc.)
      5) quadruple_collision_ammonia (N2+3H2 =>2NH3, etc.)
      6) final do_elastic_bounce
    """
    candidate_pairs = build_spatial_grid(particles, main_width, main_height)
    colliding_pairs = detect_overlapping_pairs(particles, candidate_pairs)

    # Pairwise diatomic (H+H => H2, etc.)
    pairwise_reactions_diatomic(particles, colliding_pairs)

    # Triple collisions (2H2 + O2 => 2H2O, etc.)
    triple_collision_stoich(particles, colliding_pairs)

    # Quad collisions (N2 + 3H2 => 2NH3)
    quadruple_collision_ammonia(particles, colliding_pairs)

    # Finally bounce all remaining pairs
    do_elastic_bounce(particles, colliding_pairs)


# ------------------------------------------------
# 1. BUILD SPATIAL GRID (BROADPHASE)
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
            ncx, ncy = cx+dx, cy+dy
            if (ncx, ncy) not in grid:
                continue
            for i1 in idx_list:
                for i2 in grid[(ncx,ncy)]:
                    if i1 < i2:
                        candidate_pairs.append((i1, i2))
    return candidate_pairs


# ------------------------------------------------
# 2. DETECT OVERLAPPING (BUT DON'T BOUNCE)
# ------------------------------------------------
def detect_overlapping_pairs(particles, candidate_pairs):
    colliding_pairs = set()
    for (i1, i2) in candidate_pairs:
        p1 = particles[i1]
        p2 = particles[i2]
        if are_colliding(p1, p2):
            if i1 < i2:
                colliding_pairs.add((i1, i2))
            else:
                colliding_pairs.add((i2, i1))
    return colliding_pairs

def are_colliding(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    dist_sq = dx*dx + dy*dy
    r_sum = a.radius + b.radius
    return dist_sq < r_sum*r_sum


# ------------------------------------------------
# 3. PAIRWISE REACTIONS FOR DIATOMIC (H+H => H2, etc.)
# ------------------------------------------------
def pairwise_reactions_diatomic(particles, colliding_pairs):
    """
    If (i,j) in colliding_pairs:
      - H + H => H2
      - N + N => N2
      - O + O => O2
    Remove the single atoms, spawn a new diatomic with combined mass & momentum
    """
    to_remove = set()
    to_add = []

    n = len(particles)
    # We'll do i<j approach
    for i in range(n-1):
        if i in to_remove:
            continue
        for j in range(i+1, n):
            if j in to_remove:
                continue
            if (i,j) not in colliding_pairs:
                continue
            p1 = particles[i]
            p2 = particles[j]

            # e.g. "H" + "H" => H2
            if p1.symbol=="H" and p2.symbol=="H":
                newp = combine_two(p1, p2, H2_DATA)
                to_remove.update([i,j])
                to_add.append(newp)
            elif p1.symbol=="N" and p2.symbol=="N":
                newp = combine_two(p1, p2, N2_DATA)
                to_remove.update([i,j])
                to_add.append(newp)
            elif p1.symbol=="O" and p2.symbol=="O":
                newp = combine_two(p1, p2, O2_DATA)
                to_remove.update([i,j])
                to_add.append(newp)

    # remove them from the end
    for idx in sorted(to_remove, reverse=True):
        del particles[idx]
    particles.extend(to_add)

def combine_two(a, b, data):
    """
    a.symbol + b.symbol => data["symbol"] (like H2).
    total mass = a.mass + b.mass, share momentum
    """
    m_sum = a.mass + b.mass
    vx_sum = a.vx*a.mass + b.vx*b.mass
    vy_sum = a.vy*a.mass + b.vy*b.mass
    x_cen = (a.x + b.x)*0.5
    y_cen = (a.y + b.y)*0.5

    from particle import Particle
    p = Particle(x_cen, y_cen, m_sum, data["symbol"], data["color"], data["radius"])
    p.vx = vx_sum / m_sum
    p.vy = vy_sum / m_sum
    return p


# ------------------------------------------------
# 4. TRIPLE COLLISION (2H2+O2 =>2H2O, etc.)
# ------------------------------------------------
def triple_collision_stoich(particles, colliding_pairs):
    to_remove=set()
    to_add=[]
    n= len(particles)

    for i in range(n-2):
        if i in to_remove:
            continue
        for j in range(i+1,n-1):
            if j in to_remove:
                continue
            if (i,j) not in colliding_pairs:
                continue
            for k in range(j+1,n):
                if k in to_remove:
                    continue
                if ((i,k) in colliding_pairs) and ((j,k) in colliding_pairs):
                    p1= particles[i]
                    p2= particles[j]
                    p3= particles[k]
                    syms= [p1.symbol, p2.symbol, p3.symbol]

                    # 2H2 + O2 => 2H2O
                    if syms.count("H₂")==2 and syms.count("O₂")==1:
                        to_remove.update([i,j,k])
                        new_water= spawn_two_molecules_3(p1,p2,p3, H2O_DATA)
                        to_add.extend(new_water)

                    # 2N2 + O2 => 2N2O
                    elif syms.count("N₂")==2 and syms.count("O₂")==1:
                        to_remove.update([i,j,k])
                        new_n2o= spawn_two_molecules_3(p1,p2,p3, N2O_DATA)
                        to_add.extend(new_n2o)
                    # Add more triple stoich if needed

    for idx in sorted(to_remove, reverse=True):
        del particles[idx]
    particles.extend(to_add)

def spawn_two_molecules_3(a,b,c, data):
    m_sum= a.mass+b.mass+c.mass
    vx_sum= a.vx*a.mass + b.vx*b.mass + c.vx*c.mass
    vy_sum= a.vy*a.mass + b.vy*b.mass + c.vy*c.mass
    x_cen= (a.x+b.x+c.x)/3
    y_cen= (a.y+b.y+c.y)/3

    each_mass= m_sum/2.0
    vx= vx_sum/m_sum
    vy= vy_sum/m_sum

    pA= Particle(x_cen-5,y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pB= Particle(x_cen+5,y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pA.vx= vx
    pA.vy= vy
    pB.vx= vx
    pB.vy= vy
    return [pA,pB]


# ------------------------------------------------
# 5. QUAD COLLISION (AMMONIA: N2+3H2 =>2NH3)
# ------------------------------------------------
def quadruple_collision_ammonia(particles, colliding_pairs):
    to_remove= set()
    to_add= []
    n= len(particles)
    for i in range(n-3):
        if i in to_remove:
            continue
        for j in range(i+1,n-2):
            if j in to_remove:
                continue
            if (i,j) not in colliding_pairs:
                continue
            for k in range(j+1,n-1):
                if k in to_remove:
                    continue
                if (i,k) not in colliding_pairs or (j,k) not in colliding_pairs:
                    continue
                for l in range(k+1,n):
                    if l in to_remove:
                        continue
                    if ((i,l) in colliding_pairs and
                        (j,l) in colliding_pairs and
                        (k,l) in colliding_pairs):
                        p1= particles[i]
                        p2= particles[j]
                        p3= particles[k]
                        p4= particles[l]
                        syms= [p1.symbol,p2.symbol,p3.symbol,p4.symbol]
                        if syms.count("N₂")==1 and syms.count("H₂")==3:
                            to_remove.update([i,j,k,l])
                            new_nh3= spawn_two_molecules_4(p1,p2,p3,p4, NH3_DATA)
                            to_add.extend(new_nh3)

    for idx in sorted(to_remove, reverse=True):
        del particles[idx]
    particles.extend(to_add)

def spawn_two_molecules_4(a,b,c,d, data):
    m_sum= a.mass+b.mass+c.mass+d.mass
    vx_sum= a.vx*a.mass+ b.vx*b.mass+ c.vx*c.mass+ d.vx*d.mass
    vy_sum= a.vy*a.mass+ b.vy*b.mass+ c.vy*c.mass+ d.vy*d.mass
    x_cen= (a.x+b.x+c.x+d.x)/4
    y_cen= (a.y+b.y+c.y+d.y)/4

    each_mass= m_sum/2.0
    vx= vx_sum/m_sum
    vy= vy_sum/m_sum

    pA= Particle(x_cen-5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pB= Particle(x_cen+5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pA.vx= vx
    pA.vy= vy
    pB.vx= vx
    pB.vy= vy
    return [pA,pB]


# ------------------------------------------------
# 6. FINAL BOUNCE
# ------------------------------------------------
def do_elastic_bounce(particles, colliding_pairs):
    """
    Now that we've done pairwise & multi-body reactions, 
    bounce the pairs that remain overlapping.
    """
    living = list(enumerate(particles))
    for (i1, i2) in colliding_pairs:
        if i1 < len(living) and i2 < len(living):
            (newidx1, p1) = living[i1]
            (newidx2, p2) = living[i2]
            if (p1 is None) or (p2 is None):
                continue
            if are_colliding(p1, p2):
                dx= p2.x - p1.x
                dy= p2.y - p1.y
                dist= math.sqrt(dx*dx+ dy*dy) or 1e-12
                overlap= (p1.radius+p2.radius)- dist
                if overlap>0:
                    nx= dx/dist
                    ny= dy/dist
                    # separate
                    p1.x-= nx*(overlap*0.5)
                    p1.y-= ny*(overlap*0.5)
                    p2.x+= nx*(overlap*0.5)
                    p2.y+= ny*(overlap*0.5)

                    vx_rel= p1.vx- p2.vx
                    vy_rel= p1.vy- p2.vy
                    dot= vx_rel*nx+ vy_rel*ny
                    if dot<0:
                        m1= p1.mass
                        m2= p2.mass
                        c1= (2*m2/(m1+m2))* dot
                        p1.vx-= c1*nx
                        p1.vy-= c1*ny
                        c2= (2*m1/(m1+m2))* dot
                        p2.vx+= c2*nx
                        p2.vy+= c2*ny
