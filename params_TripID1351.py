#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 23:10:59 2020
This code is part of SIMROUTE
@author: manel grifoll (UPC-BarcelonaTech)
"""
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Simulation name
name_Simu = 'TripID_1351'  #SOUTH EAST FROM PALMA --> WEST FROM FRANCE (CELTIC SEA)
prod = 'GLOBAL'

# Trip dates
date_Ini = [2021, 9, 29]  # [year,month,day]
date_End = [2021, 10, 4]

# Starting and ending coordinates
start_lon, start_lat = 7.330657405963223, 37.60749174780924
end_lon, end_lat = -5.649139448495825, 48.72385639119045

# Mesh boundaries with extension
mesh_extension = 1.5  # degrees

LonMin = min(start_lon, end_lon) - mesh_extension
LonMax = max(start_lon, end_lon) + mesh_extension
LatMin = min(start_lat, end_lat) - mesh_extension
LatMax = max(start_lat, end_lat) + mesh_extension

print("\nMesh boundaries:")
print(f"LonMin: {LonMin}")
print(f"LonMax: {LonMax}")
print(f"LatMin: {LatMin}")
print(f"LatMax: {LatMax}\n")

# ---------------------------
# Grid parameters
# ---------------------------

# Grid-step in Miles
inc = 12    # in nautical miles
# Extension added at boundaries (in degrees)
dx = 0.5
inc_deg = inc / 60.0  # convert nautical miles to degrees
# Number of nodes along longitude
Nx = int(np.floor((LonMax - LonMin) / inc_deg) + 2)


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


# ---------------------------
# Initial and final nodes
# ---------------------------

# Initial and final nodes (to be obtained from find_ports.py or coord_to_node)
#nodIni = coord_to_node(start_lon, start_lat)
nodIni = 639   # placeholder, replace with actual node from find_ports
#nodEnd = coord_to_node(end_lon, end_lat)
nodEnd = 5110  # placeholder, replace with actual node from find_ports

print(f"Initial node (start): {nodIni}")
print(f"Final node (end): {nodEnd}\n")

# Time resolution of CMEMS product
time_res = 3  # In hours: 1 for local regions, 3 for GLOBAL

# Directory for wave data
dir_arx = 'storeWaves/'

t_ini=7

#coastline source file:
#arx_ldc= 'in/lcd_eu_h.dat'

#coastline name output:
#    lcd_out= 'in/ldcK1.npz'

#Sailing velocity (in knots)
v0=12.58 # Cruising speed in nautical milles per hour (in knots)

#Formulation WEN (Wave Effect on Navigation)
    #Bowditch = 1; Aertessen = 2; Khokhlov = 3; no reduction = 4
WEN_form=3;

# Ship parameters for WEN options 2 and 3
Lbp = 225  # ship's length between perpendiculars (in meters)
DWT = 8000  # ship's deadweight (in tons)

# Additional plot flags
plot_nodes = 1  # Yes=1 ; No=0
plot_waves = 1  # Yes=1 ; No=0
plot_routes = 1  # Yes=1 ; No=0

# END OF USER INPUTS #######################