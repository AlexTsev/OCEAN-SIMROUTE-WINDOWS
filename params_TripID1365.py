#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 23:10:59 2020
Code part of SIMROUTE (UPC-BarcelonaTech)
Version: 02 / 03 / 21
@author: manel grifoll (UPC-BarcelonaTech)
"""
import numpy  as np
from pathlib import Path
import matplotlib.pyplot as plt

# Simulation name
name_Simu = 'TripID_1365'  # Caribbean Sea, Coast of Martinique --> Gulf of Mexico
prod = 'GLOBAL'

# Trip dates
date_Ini = [2022, 3, 7]   # [year, month, day]
date_End = [2022, 3, 13]

# Starting and ending coordinates
start_lon, start_lat = -61.22878542394138, 14.597773738775588
end_lon, end_lat = -91.50521869499202, 25.25411017987707

# Mesh boundaries with extension
mesh_extension = 1.0  # degrees
LonMin = min(start_lon, end_lon) - mesh_extension
LonMax = max(start_lon, end_lon) + mesh_extension
LatMin = min(start_lat, end_lat) - mesh_extension
LatMax = max(start_lat, end_lat) + mesh_extension

print("\nMesh boundaries:")
print(f"LonMin: {LonMin}")
print(f"LonMax: {LonMax}")
print(f"LatMin: {LatMin}")
print(f"LatMax: {LatMax}\n")

# Grid-step in nautical miles
inc = 2
inc_deg = inc / 60.0  # convert to degrees

# Extension added at boundaries (in degrees)
dx = 0.5

# Number of nodes along longitude
Nx = int(np.floor((LonMax - LonMin) / inc_deg) + 2)

# ------------------ FUNCTIONS ------------------
# ---------------------------
# coord_to_node function with debug and bounds check
# ---------------------------
def coord_to_node(lon, lat):
    """
    Convert longitude/latitude to mesh node with bounds checks.
    """
    # Check if coordinates are inside mesh
    if not (LonMin <= lon <= LonMax):
        raise ValueError(f"Longitude {lon} out of bounds [{LonMin}, {LonMax}]")
    if not (LatMin <= lat <= LatMax):
        raise ValueError(f"Latitude {lat} out of bounds [{LatMin}, {LatMax}]")

    # Convert to node indices
    i = int(np.floor((lon - LonMin) / inc_deg))
    j = int(np.floor((lat - LatMin) / inc_deg))
    node = j * Nx + i

    # Debug info
    print(f"coord_to_node debug: lon={lon}, lat={lat}, i={i}, j={j}, node={node}")

    return node

# ------------------ INITIAL/FINAL NODES ------------------

# Initial node in mesh
#nodIni = coord_to_node(start_lon, start_lat)
nodIni = 30038

# Final node in mesh
#nodEnd = coord_to_node(end_lon, end_lat)
nodEnd = 338560

print(f"Initial node (start): {nodIni}")
print(f"Final node (end): {nodEnd}\n")

# ------------------ SIMULATION PARAMETERS ------------------

dir_arx = 'storeWaves/'

# Time resolution of CMEMS product
time_res = 3  # hours: 1 for local regions, 3 for GLOBAL

# Wave interpolated file (output)
arx_waves = 'in/waves.npz'

# Initial start time of sailing (hour)
t_ini = 13

# Sailing velocity (knots)
v0 = 12.77

# Formulation WEN (Wave Effect on Navigation)
# 1=Bowditch, 2=Aertessen, 3=Khokhlov, 4=no reduction
WEN_form = 3

# Ship parameters for WEN options 2 and 3
Lbp = 225   # ship's length between perpendiculars (m)
DWT = 8000  # ship's deadweight (tons)

# Plot flags
plot_nodes = 1
plot_waves = 1
plot_routes = 1

# END OF USER INPUTS ########################