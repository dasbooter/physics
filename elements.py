"""
Holds all element and compound data, plus a more standard periodic table arrangement.
The arrange_periodic_table() function below is used to position elements as in the real periodic table.
"""

# Special single-atom data for period 1 and 2 (and a few others)
SPECIAL_ATOMS = {
    1:  {"symbol": "H",  "atomic_mass": 1,   "color": (255, 0, 0),       "radius": 6},
    2:  {"symbol": "He", "atomic_mass": 4,   "color": (200, 200, 255),   "radius": 6},
    3:  {"symbol": "Li", "atomic_mass": 7,   "color": (200, 200, 200),   "radius": 6},
    4:  {"symbol": "Be", "atomic_mass": 9,   "color": (0, 255, 0),       "radius": 6},
    5:  {"symbol": "B",  "atomic_mass": 11,  "color": (255, 200, 0),     "radius": 6},
    6:  {"symbol": "C",  "atomic_mass": 12,  "color": (80, 80, 80),      "radius": 7},
    7:  {"symbol": "N",  "atomic_mass": 14,  "color": (100, 100, 255),   "radius": 7},
    8:  {"symbol": "O",  "atomic_mass": 16,  "color": (255, 100, 100),   "radius": 7},
    9:  {"symbol": "F",  "atomic_mass": 19,  "color": (0, 255, 255),     "radius": 6},
    10: {"symbol": "Ne", "atomic_mass": 20,  "color": (200, 200, 200),   "radius": 6},
    11: {"symbol": "Na", "atomic_mass": 23,  "color": (170, 170, 255),   "radius": 6},
    12: {"symbol": "Mg", "atomic_mass": 24,  "color": (170, 255, 170),   "radius": 6},
}

# Define additional compounds used in reactions.
COMPOUND_DATA = {
    # Existing compounds
    "H₂":  {"symbol": "H₂",  "mass": 2,    "color": (255, 50, 50),    "radius": 7},
    "O₂":  {"symbol": "O₂",  "mass": 32,   "color": (255, 150, 150),  "radius": 8},
    "N₂":  {"symbol": "N₂",  "mass": 28,   "color": (150, 150, 255),  "radius": 8},
    "H₂O": {"symbol": "H₂O", "mass": 18,   "color": (0, 0, 255),      "radius": 9},
    "N₂O": {"symbol": "N₂O", "mass": 44,   "color": (100, 200, 255),  "radius": 10},
    "NO":  {"symbol": "NO",  "mass": 30,   "color": (200, 200, 100),  "radius": 8},
    "NH₃": {"symbol": "NH₃", "mass": 17,   "color": (100, 255, 100),  "radius": 8},
    "CO":  {"symbol": "CO",  "mass": 28,   "color": (200, 200, 200),  "radius": 7},
    "CO₂": {"symbol": "CO₂", "mass": 44,   "color": (80, 200, 80),    "radius": 8},
    "NO₂": {"symbol": "NO₂", "mass": 46,   "color": (200, 180, 120),  "radius": 8},
    "CH₄": {"symbol": "CH₄", "mass": 16,   "color": (200, 255, 200),  "radius": 7},
    # Helium compounds
    "He₂": {"symbol": "He₂", "mass": 8,    "color": (210, 210, 255),  "radius": 6},
    "HeH": {"symbol": "HeH", "mass": 5,    "color": (230, 230, 255),  "radius": 6},
    # Lithium compounds
    "Li₂": {"symbol": "Li₂", "mass": 14,   "color": (220, 220, 220),  "radius": 6},
    "LiH": {"symbol": "LiH", "mass": 8,    "color": (240, 240, 240),  "radius": 6},
    # Beryllium compounds
    "Be₂": {"symbol": "Be₂", "mass": 18,   "color": (180, 255, 180),  "radius": 6},
    "BeO": {"symbol": "BeO", "mass": 25,   "color": (100, 255, 100),  "radius": 7},
    # New compounds for period 2:
    "B₂":  {"symbol": "B₂",  "mass": 22,   "color": (255, 220, 100),  "radius": 6},
    "F₂":  {"symbol": "F₂",  "mass": 38,   "color": (0, 255, 255),    "radius": 7},
    "BF":  {"symbol": "BF",  "mass": 30,   "color": (255, 160, 50),   "radius": 7},
    "NeF": {"symbol": "NeF", "mass": 39,   "color": (220, 220, 255),  "radius": 7},
}

# Global dictionary for the periodic table.
PERIODIC_TABLE_ATOMS = {}

def build_periodic_table():
    """
    Build a standard arrangement using arrange_periodic_table() for positions.
    """
    for Z in range(1, 119):
        if Z in SPECIAL_ATOMS:
            sdata = SPECIAL_ATOMS[Z]
            symbol = sdata["symbol"]
            mass   = sdata["atomic_mass"]
            color  = sdata["color"]
            radius = sdata["radius"]
        else:
            symbol = f"El{Z}"
            mass   = 50
            color  = (150, 150, 150)
            radius = 8

        row, col = arrange_periodic_table(Z)
        PERIODIC_TABLE_ATOMS[Z] = {
            "symbol": symbol,
            "atomic_mass": mass,
            "color": color,
            "radius": radius,
            "row": row,
            "col": col,
        }

def arrange_periodic_table(Z):
    """
    Returns (row, col) for each atomic number, following the real periodic table layout.
    Adjusted row positioning to lower elements visually for better alignment.
    """
    SPECIAL_LAYOUT = {
        1:  (1, 0),   # Hydrogen
        2:  (1, 17),  # Helium
        3:  (2, 0),   # Li
        4:  (2, 1),   # Be
        5:  (2, 12),  # B
        6:  (2, 13),  # C
        7:  (2, 14),  # N
        8:  (2, 15),  # O
        9:  (2, 16),  # F
        10: (2, 17),  # Ne
        11: (3, 0),   # Na
        12: (3, 1),   # Mg
        13: (3, 12),  # Al
        14: (3, 13),  # Si
        15: (3, 14),  # P
        16: (3, 15),  # S
        17: (3, 16),  # Cl
        18: (3, 17),  # Ar
    }
    
    if Z in SPECIAL_LAYOUT:
        return SPECIAL_LAYOUT[Z]
    
    # Lanthanides (57-71) and Actinides (89-103) go in separate rows
    if 57 <= Z <= 71:
        return (7, Z - 57 + 2)  # Row 7, Columns 2-16
    if 89 <= Z <= 103:
        return (8, Z - 89 + 2)  # Row 8, Columns 2-16
    
    # Transition Metals: Fill middle section
    if 21 <= Z <= 30:
        return (4, Z - 21 + 2)  # Row 4, Columns 2-11
    if 39 <= Z <= 48:
        return (5, Z - 39 + 2)  # Row 5, Columns 2-11
    if 57 <= Z <= 80:
        return (6, (Z - 57) % 18 + 2)  # Row 6, Offset for transition metals
    if 89 <= Z <= 112:
        return (7, (Z - 89) % 18 + 2)  # Row 7, Offset for transition metals
    
    # Normal rows after special layout
    row = (Z - 1) // 18 + 2  # Shift down by adding +2 to rows
    col = (Z - 1) % 18
    return (row, col)

# Common compound names.
COMPOUND_COMMON_NAMES = {
    "H₂":  "Dihydrogen",
    "O₂":  "Dioxygen",
    "N₂":  "Dinitrogen",
    "H₂O": "Water",
    "N₂O": "Nitrous Oxide",
    "NO":  "Nitric Oxide",
    "NH₃": "Ammonia",
    "CO":  "Carbon Monoxide",
    "CO₂": "Carbon Dioxide",
    "NO₂": "Nitrogen Dioxide",
    "CH₄": "Methane",
    "He₂": "Helium Dimer",
    "HeH": "Helium Hydride",
    "Li₂": "Lithium Dimer",
    "LiH": "Lithium Hydride",
    "Be₂": "Beryllium Dimer",
    "BeO": "Beryllium Oxide",
    "B₂":  "Boron Dimer",
    "F₂":  "Fluorine Gas",
    "BF":  "Boron Monofluoride",
    "NeF": "Neon Fluoride",
}

# For convenience, export individual compound data names.
H2_DATA   = COMPOUND_DATA["H₂"]
O2_DATA   = COMPOUND_DATA["O₂"]
N2_DATA   = COMPOUND_DATA["N₂"]
H2O_DATA  = COMPOUND_DATA["H₂O"]
N2O_DATA  = COMPOUND_DATA["N₂O"]
NO_DATA   = COMPOUND_DATA["NO"]
NH3_DATA  = COMPOUND_DATA["NH₃"]
CO_DATA   = COMPOUND_DATA["CO"]
CO2_DATA  = COMPOUND_DATA["CO₂"]
NO2_DATA  = COMPOUND_DATA["NO₂"]
CH4_DATA  = COMPOUND_DATA["CH₄"]
HE2_DATA  = COMPOUND_DATA["He₂"]
HEH_DATA  = COMPOUND_DATA["HeH"]
LI2_DATA  = COMPOUND_DATA["Li₂"]
LIH_DATA  = COMPOUND_DATA["LiH"]
BE2_DATA  = COMPOUND_DATA["Be₂"]
BEO_DATA  = COMPOUND_DATA["BeO"]
B2_DATA   = COMPOUND_DATA["B₂"]
F2_DATA   = COMPOUND_DATA["F₂"]
BF_DATA   = COMPOUND_DATA["BF"]
NEF_DATA  = COMPOUND_DATA["NeF"]
