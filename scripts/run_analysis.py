"""
run bridge analysis on a design
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cross_section_geometry.designs import simple_square
from src.cross_section_geometry.analysis import analyze_design

geometry = simple_square()
results = analyze_design(
    geometry=geometry,
    loadcase=1,
    mass=400,
    output_dir='output/simple_square'
)

print(f"\nAnalysis done!!! Failure load: {results['failure_load']} N")
