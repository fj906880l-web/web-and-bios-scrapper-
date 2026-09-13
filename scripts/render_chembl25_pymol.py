#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = [
#     "pymol-open-source-whl",
# ]
# ///
"""
PyMOL Headless 3D Molecular Structure Rendering for CHEMBL25
=============================================================
Uses software OSMesa rendering for headless container and CI/CD pipelines.
Exports publication-quality PNG and reproducible PyMOL session (.pse).
"""
import os
import sys

# Set environment variable for headless software rendering
os.environ["PYOPENGL_PLATFORM"] = "osmesa"

import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()

from pymol import cmd

# Dynamic repository relative structure path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
structure_file = os.path.join(repo_root, "data", "CHEMBL25.sdf")
if not os.path.exists(structure_file):
    print(f"Error: Structure file not found: {structure_file}")
    cmd.quit()
    sys.exit(1)

cmd.load(structure_file, "compound_chembl25")
atom_count = cmd.count_atoms("all")
if atom_count == 0:
    print("Error: 0 atoms loaded from structure file")
    cmd.quit()
    sys.exit(1)

print(f"[+] Loaded {atom_count} atoms for CHEMBL25")
cmd.show("sticks", "all")
cmd.color("cyan", "elem C")
cmd.color("red", "elem O")
cmd.color("blue", "elem N")
cmd.orient()
cmd.set("ray_opaque_background", 0)

output_png = os.path.join(os.path.dirname(structure_file), "chembl25_3d.png")
output_pse = os.path.join(os.path.dirname(structure_file), "chembl25_session.pse")

cmd.png(output_png, width=1200, height=900, dpi=150)
cmd.save(output_pse)
print(f"[+] Rendered 3D structure to {output_png} and saved session to {output_pse}")
cmd.quit()
