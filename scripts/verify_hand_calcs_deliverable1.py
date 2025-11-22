"""
verify hand calculations for deliverable 1

uses design0 cross section with loadcase 1, 400N mass, first wheel at 172 mm
prints section properties, reactions, SFD, BMD, flexural stresses, and FOS
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.cross_section_geometry.designs import design0
from src.core.geometric_properties import y_bar, I, Q, width
from src.core.reactions_BMD_SFD import reactions, SFDvals, BMDvals
from src.core.stresses import sigma_top, sigma_bot
from src.materials.material_properties import get_matboard_properties
import matplotlib.pyplot as plt

# get design0 geometry
geometry = design0()
plates = geometry['plates']

# section properties
ybar = y_bar(plates)
I_val = I(plates)
total_area = sum(plate['b'] * plate['h'] for plate in plates)

print("design 0 hand calc verification")
print("loadcase 1, 400N, first wheel at 172mm")
print()

print("section properties:")
print(f"A = {total_area} mm^2")
print(f"ybar = {ybar} mm from bottom")
print(f"I = {I_val} mm^4")
print()

# load configuration
loadcase = 1
mass = 400  # N
first_wheel_position = 172  # mm from left edge

# calculate reactions
RA, RB = reactions(first_wheel_position, loadcase, mass)
print("support reactions:")
print(f"RA (at 25mm) = {RA} N")
print(f"RB (at 1225mm) = {RB} N")
print(f"sum = {RA + RB} N (should be {mass})")
print()

# get SFD and BMD
sfd = SFDvals(first_wheel_position, loadcase, mass)
bmd = BMDvals(first_wheel_position, loadcase, mass)

# find max moment and its location
max_moment = max(bmd)
max_moment_index = bmd.index(max_moment)
min_moment = min(bmd)
min_moment_index = bmd.index(min_moment)

# find max/min shear
max_shear = max(sfd)
max_shear_index = sfd.index(max_shear)
min_shear = min(sfd)
min_shear_index = sfd.index(min_shear)

bridge_length = 1250
num_points = 10000
max_moment_location = max_moment_index * bridge_length / (num_points - 1)
min_moment_location = min_moment_index * bridge_length / (num_points - 1)
max_shear_location = max_shear_index * bridge_length / (num_points - 1)
min_shear_location = min_shear_index * bridge_length / (num_points - 1)

print("shear force diagram (SFD):")
print(f"max shear = {max_shear} N at x = {max_shear_location} mm")
print(f"min shear = {min_shear} N at x = {min_shear_location} mm")
print()

print("bending moment diagram (BMD):")
print(f"Mmax = {max_moment} N*mm at x = {max_moment_location} mm")
print(f"Mmin = {min_moment} N*mm at x = {min_moment_location} mm")
print()

# calculate stresses at max moment location
# top of section
y_top = max(plate['y'] + plate['h']/2 for plate in plates)
# bottom of section
y_bot = ybar  # distance from neutral axis to bottom fiber

sigma_t = sigma_top(max_moment, y_top, I_val)
sigma_b = sigma_bot(max_moment, y_bot, I_val)

print("flexural stresses at Mmax:")
print(f"distance from NA to top = {y_top - ybar} mm")
print(f"distance from NA to bottom = {y_bot} mm")
print(f"sigma_top = {sigma_t} MPa (compression)")
print(f"sigma_bot = {sigma_b} MPa (tension)")
print()

# get material properties
matboard = get_matboard_properties()
sigma_tens_max = matboard['sigma_tens']
sigma_comp_max = matboard['sigma_comp']

print("material capacities:")
print(f"tensile strength = {sigma_tens_max} MPa")
print(f"compressive strength = {sigma_comp_max} MPa")
print()

# calculate FOS
# top is in compression (negative stress)
FOS_top_compression = sigma_comp_max / abs(sigma_t) if abs(sigma_t) > 1e-9 else float('inf')
# bottom is in tension (positive stress)
FOS_bottom_tension = sigma_tens_max / abs(sigma_b) if abs(sigma_b) > 1e-9 else float('inf')

print("factor of safety:")
print(f"FOS compression (top) = {FOS_top_compression}")
print(f"FOS tension (bottom) = {FOS_bottom_tension}")
print()

# plot SFD and BMD
positions = [i * bridge_length / (num_points - 1) for i in range(num_points)]

# create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# plot SFD
ax1.plot(positions, sfd, 'b-', linewidth=1.5)
ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax1.axvline(x=25, color='r', linestyle='--', linewidth=0.8, alpha=0.5, label='Support A')
ax1.axvline(x=1225, color='r', linestyle='--', linewidth=0.8, alpha=0.5, label='Support B')
ax1.grid(True, alpha=0.3)
ax1.set_xlabel('Position along bridge (mm)')
ax1.set_ylabel('Shear Force (N)')
ax1.set_title('Shear Force Diagram (SFD) - Design 0, Loadcase 1, 400N, first wheel at 172mm')
ax1.legend()

# plot BMD
ax2.plot(positions, bmd, 'r-', linewidth=1.5)
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax2.axvline(x=25, color='r', linestyle='--', linewidth=0.8, alpha=0.5, label='Support A')
ax2.axvline(x=1225, color='r', linestyle='--', linewidth=0.8, alpha=0.5, label='Support B')
ax2.grid(True, alpha=0.3)
ax2.set_xlabel('Position along bridge (mm)')
ax2.set_ylabel('Bending Moment (N*mm)')
ax2.set_title('Bending Moment Diagram (BMD) - Design 0, Loadcase 1, 400N, first wheel at 172mm')
ax2.legend()

plt.tight_layout()

# save the plot
output_path = Path(__file__).parent.parent / 'not_code' / 'images_for_calc_report' / 'SFD_BMD_design0_loadcase1_172mm.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"saved plot to {output_path}")
plt.close()
