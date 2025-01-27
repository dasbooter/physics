# elements.py
"""
Holds all element and compound data, plus periodic table info.
"""

# A few special single atoms with real data:
SPECIAL_ATOMS = {
    1:  {"symbol": "H", "atomic_mass": 1,  "color": (255, 0, 0),    "radius": 6},
    7:  {"symbol": "N", "atomic_mass": 14, "color": (100, 100, 255),"radius": 7},
    8:  {"symbol": "O", "atomic_mass": 16, "color": (255, 100, 100),"radius": 7},
}

# We'll build a dictionary PERIODIC_TABLE_ATOMS for Z=1..118
# We do a naive 18 columns, 7 rows approach for layout in a bottom UI.
PERIODIC_TABLE_ATOMS = {} 
def build_periodic_table():
    for Z in range(1, 119):
        if Z in SPECIAL_ATOMS:
            sdata = SPECIAL_ATOMS[Z]
            symbol = sdata["symbol"]
            mass   = sdata["atomic_mass"]
            color  = sdata["color"]
            radius = sdata["radius"]
        else:
            # placeholder
            symbol = f"El{Z}"
            mass   = 50
            color  = (150, 150, 150)
            radius = 8
        
        # row/col in an 18-col layout
        row = (Z - 1) // 18 + 1
        col = (Z - 1) % 18 + 1

        PERIODIC_TABLE_ATOMS[Z] = {
            "symbol": symbol,
            "atomic_mass": mass,
            "color": color,
            "radius": radius,
            "row": row,
            "col": col,
        }

# Compound data
H2_DATA  = {"symbol": "H₂",  "mass": 2,   "color": (255, 50, 50),   "radius": 7}
O2_DATA  = {"symbol": "O₂",  "mass": 32,  "color": (255, 150, 150), "radius": 8}
N2_DATA  = {"symbol": "N₂",  "mass": 28,  "color": (150, 150, 255), "radius": 8}
H2O_DATA = {"symbol": "H₂O", "mass": 18,  "color": (0, 0, 255),      "radius": 9}
N2O_DATA = {"symbol": "N₂O", "mass": 44,  "color": (100, 200, 255), "radius": 10}
NO_DATA  = {"symbol": "NO",  "mass": 30,  "color": (200, 200, 100), "radius": 8}
NH3_DATA = {"symbol": "NH₃", "mass": 17,  "color": (100, 255, 100), "radius": 8}

# Common names
COMPOUND_COMMON_NAMES = {
    "H₂":  "Dihydrogen",
    "O₂":  "Dioxygen",
    "N₂":  "Dinitrogen",
    "H₂O": "Water",
    "N₂O": "Nitrous Oxide",
    "NO":  "Nitric Oxide",
    "NH₃": "Ammonia",
}
