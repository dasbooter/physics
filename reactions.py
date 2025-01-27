# reactions.py
"""
Handles collisions (elastic overlap) and chemical reactions:
  - diatomic formation
  - triple collisions (2H2 + O2 => 2H2O, etc.)
  - quadruple collisions (N2 + 3H2 => 2NH3)
"""

import math
from elements import (H2_DATA, O2_DATA, N2_DATA, H2O_DATA, N2O_DATA, NO_DATA, NH3_DATA)
from particle import Particle

def resolve_collisions(particles):
    quadruple_collision_ammonia(particles)
    triple_collision_stoich(particles)
    pairwise_collisions(particles)
    pairwise_reactions_diatomic(particles)
    pairwise_reactions_n2o2_to_no(particles)

def quadruple_collision_ammonia(particles):
    # N2 + 3H2 => 2NH3
    to_remove = set()
    to_add = []
    n = len(particles)
    for i in range(n - 3):
        p1 = particles[i]
        if p1 in to_remove:
            continue
        for j in range(i+1, n - 2):
            p2 = particles[j]
            if p2 in to_remove:
                continue
            for k in range(j+1, n - 1):
                p3 = particles[k]
                if p3 in to_remove:
                    continue
                for l in range(k+1, n):
                    p4 = particles[l]
                    if p4 in to_remove:
                        continue

                    # check if all four overlap pairwise
                    if all_four_collide(p1,p2,p3,p4):
                        syms = [p1.symbol, p2.symbol, p3.symbol, p4.symbol]
                        if syms.count("N₂")==1 and syms.count("H₂")==3:
                            to_remove.update([p1,p2,p3,p4])
                            new_nh3 = spawn_two_molecules_4(p1,p2,p3,p4, NH3_DATA)
                            to_add.extend(new_nh3)

    for r in to_remove:
        if r in particles:
            particles.remove(r)
    particles.extend(to_add)

def spawn_two_molecules_4(a,b,c,d, data):
    # total mass/momentum
    m_sum = a.mass + b.mass + c.mass + d.mass
    vx_sum= a.vx*a.mass + b.vx*b.mass + c.vx*c.mass + d.vx*d.mass
    vy_sum= a.vy*a.mass + b.vy*b.mass + c.vy*c.mass + d.vy*d.mass

    x_cen= (a.x + b.x + c.x + d.x)/4
    y_cen= (a.y + b.y + c.y + d.y)/4

    each_mass= m_sum/2.0
    vx= vx_sum / m_sum
    vy= vy_sum / m_sum

    pA= Particle(x_cen-5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pB= Particle(x_cen+5, y_cen, each_mass, data["symbol"], data["color"], data["radius"])
    pA.vx= vx
    pA.vy= vy
    pB.vx= vx
    pB.vy= vy
    return [pA,pB]

def all_four_collide(p1,p2,p3,p4):
    return (are_colliding(p1,p2) and are_colliding(p1,p3) and are_colliding(p1,p4) and
            are_colliding(p2,p3) and are_colliding(p2,p4) and are_colliding(p3,p4))

# Triple collisions (2H2 + O2 => 2H2O, etc.)
def triple_collision_stoich(particles):
    to_remove = set()
    to_add = []
    n = len(particles)
    for i in range(n - 2):
        p1 = particles[i]
        if p1 in to_remove:
            continue
        for j in range(i+1, n - 1):
            p2 = particles[j]
            if p2 in to_remove:
                continue
            for k in range(j+1, n):
                p3 = particles[k]
                if p3 in to_remove:
                    continue
                if all_three_collide(p1,p2,p3):
                    syms= [p1.symbol,p2.symbol,p3.symbol]
                    # 2H2 + O2 => 2H2O
                    if syms.count("H₂")==2 and syms.count("O₂")==1:
                        to_remove.update([p1,p2,p3])
                        new_water= spawn_two_molecules_3(p1,p2,p3, H2O_DATA)
                        to_add.extend(new_water)
                    # 2N2 + O2 => 2N2O
                    elif syms.count("N₂")==2 and syms.count("O₂")==1:
                        to_remove.update([p1,p2,p3])
                        new_n2o= spawn_two_molecules_3(p1,p2,p3, N2O_DATA)
                        to_add.extend(new_n2o)
    for r in to_remove:
        if r in particles:
            particles.remove(r)
    particles.extend(to_add)

def all_three_collide(a,b,c):
    return (are_colliding(a,b) and are_colliding(a,c) and are_colliding(b,c))

def spawn_two_molecules_3(a,b,c, data):
    m_sum= a.mass+b.mass+c.mass
    vx_sum= a.vx*a.mass + b.vx*b.mass + c.vx*c.mass
    vy_sum= a.vy*a.mass + b.vy*b.mass + c.vy*c.mass
    x_cen= (a.x+b.x+c.x)/3
    y_cen= (a.y+b.y+c.y)/3

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

# Pairwise collisions (elastic overlap)
def pairwise_collisions(particles):
    n= len(particles)
    for i in range(n-1):
        for j in range(i+1,n):
            p1= particles[i]
            p2= particles[j]
            if are_colliding(p1,p2):
                dx= p2.x - p1.x
                dy= p2.y - p1.y
                dist= math.sqrt(dx*dx + dy*dy) or 1e-12
                overlap= (p1.radius + p2.radius) - dist
                nx= dx/dist
                ny= dy/dist

                # separate
                p1.x -= nx*(overlap*0.5)
                p1.y -= ny*(overlap*0.5)
                p2.x += nx*(overlap*0.5)
                p2.y += ny*(overlap*0.5)

                # 1D elastic collision
                vx_rel= p1.vx - p2.vx
                vy_rel= p1.vy - p2.vy
                dot= vx_rel*nx + vy_rel*ny
                if dot<0:
                    m1= p1.mass
                    m2= p2.mass
                    c1= (2*m2/(m1+m2))*dot
                    p1.vx -= c1*nx
                    p1.vy -= c1*ny
                    c2= (2*m1/(m1+m2))*dot
                    p2.vx += c2*nx
                    p2.vy += c2*ny

def are_colliding(a,b):
    dx= b.x-a.x
    dy= b.y-a.y
    dist_sq= dx*dx + dy*dy
    r_sum= a.radius+b.radius
    return dist_sq< r_sum*r_sum

# Pairwise reactions for diatomic formation
def pairwise_reactions_diatomic(particles):
    to_remove= set()
    to_add= []
    n= len(particles)
    for i in range(n-1):
        p1= particles[i]
        if p1 in to_remove:
            continue
        for j in range(i+1,n):
            p2= particles[j]
            if p2 in to_remove:
                continue
            if not are_colliding(p1,p2):
                continue

            # H+H => H2
            if p1.symbol=="H" and p2.symbol=="H":
                newp= combine_two(p1,p2, H2_DATA)
                to_remove.update([p1,p2])
                to_add.append(newp)
            # O+O => O2
            elif p1.symbol=="O" and p2.symbol=="O":
                newp= combine_two(p1,p2, O2_DATA)
                to_remove.update([p1,p2])
                to_add.append(newp)
            # N+N => N2
            elif p1.symbol=="N" and p2.symbol=="N":
                newp= combine_two(p1,p2, N2_DATA)
                to_remove.update([p1,p2])
                to_add.append(newp)

    for r in to_remove:
        if r in particles:
            particles.remove(r)
    particles.extend(to_add)

def combine_two(a,b,data):
    m_sum= a.mass + b.mass
    vx_sum= a.vx*a.mass + b.vx*b.mass
    vy_sum= a.vy*a.mass + b.vy*b.mass
    x_cen= (a.x+b.x)*0.5
    y_cen= (a.y+b.y)*0.5

    p= Particle(x_cen, y_cen, m_sum, data["symbol"], data["color"], data["radius"])
    p.vx= vx_sum/m_sum
    p.vy= vy_sum/m_sum
    return p

# Additional reaction: N2 + O2 => 2NO
def pairwise_reactions_n2o2_to_no(particles):
    to_remove= set()
    to_add= []
    n= len(particles)
    for i in range(n-1):
        p1= particles[i]
        if p1 in to_remove:
            continue
        for j in range(i+1,n):
            p2= particles[j]
            if p2 in to_remove:
                continue
            if not are_colliding(p1,p2):
                continue

            # N2 + O2 => 2 NO
            if (p1.symbol=="N₂" and p2.symbol=="O₂") or (p1.symbol=="O₂" and p2.symbol=="N₂"):
                new_nos= spawn_two_molecules_pair(p1,p2, NO_DATA)
                to_remove.update([p1,p2])
                to_add.extend(new_nos)

    for r in to_remove:
        if r in particles:
            particles.remove(r)
    particles.extend(to_add)

def spawn_two_molecules_pair(a,b,data):
    m_sum= a.mass + b.mass
    vx_sum= a.vx*a.mass + b.vx*b.mass
    vy_sum= a.vy*a.mass + b.vy*b.mass
    x_cen= (a.x+b.x)*0.5
    y_cen= (a.y+b.y)*0.5

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
