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

#Simulation name
name_Simu = 'TripID_1398' #WEST OF INDIA (SW OF GUJARAT) --> SOUTH EAST OF BRAZIL(SOUTH EAST OF RIO DE JANEIRO)
prod = 'GLOBAL'

date_Ini = [2023, 4, 6]  # [year,month,day]
date_End = [2023 , 5, 5]

# Starting and ending coordinates
start_lon, start_lat = 69.69871307204315, 22.622512804025988
end_lon, end_lat = -35.763883893187845, -26.15147743658466

# Calculate mesh boundaries (with extension)
mesh_extension = 2  # degrees

#calculate Longmin,Lonmax,Latmin,Latmax + Mesh boundaries
LonMin = min(start_lon, end_lon) - mesh_extension
LonMax = max(start_lon, end_lon) + mesh_extension
LatMin = min(start_lat, end_lat) - mesh_extension
LatMax = max(start_lat, end_lat) + mesh_extension

print("\nMesh boundaries:")
print(f"LonMin: {LonMin}")
print(f"LonMax: {LonMax}")
print(f"LatMin: {LatMin}")
print(f"LatMax: {LatMax}\n")


#Grid-step in Miles
inc=12    #in nautical miles

#Extension added at boundaries (in degrees)
#dx= 2
dx = inc/10

Nx = int((LonMax - LonMin) / dx) + 1

"""
def coord_to_node(lon, lat):
    i = round((lon - LonMin) / dx)
    j = round((lat - LatMin) / dx)
    return j * Nx + i
"""
def coord_to_node(lon, lat):
    # convert coordinates to grid indices
    i = int((lon - LonMin) / dx)
    j = int((lat - LatMin) / dx)

    # Έλεγχος ορίων για να μην βγει εκτός grid
    if i < 0:
        i = 0
    if j < 0:
        j = 0
    if i >= Nx:
        i = Nx - 1

    Ny = int((LatMax - LatMin) / dx) + 1
    if j >= Ny:
        j = Ny - 1

    # convert to node index
    node = j * Nx + i

    return node

# Initial node in mesh:
nodIni = coord_to_node(start_lon, start_lat) #[7.33,37.60]
# Final node in mesh:
nodEnd = coord_to_node(end_lon, end_lat) #[-5.64,48.72]

print(f"Initial node (start): {nodIni}")
print(f"Final node (end): {nodEnd}")

dir_arx='storeWaves/'

#Time resolution of CMEMS product:
time_res=3 # In hours: 1 for all regions except o 3 for the GLOBAL

#Wave interpolated file (output):
arx_waves= 'in/waves.npz'

#Initial start time of sailing from 00:00 (from 0 to 23 hours)
t_ini=6

#coastline source file:
#arx_ldc= 'in/lcd_eu_h.dat'

#coastline name output:
#    lcd_out= 'in/ldcK1.npz'

#Sailing velocity (in knots)
v0=12.03  # Cruising speed in nautical milles per hour (in knots)

#Formulation WEN (Wave Effect on Navigation)
    #Bowditch = 1; Aertessen = 2; Khokhlov = 3; no reduction = 4
WEN_form=1;

#Ship parameteres for WEN options 2 and 3.
Lbp = 225; # ship's length between perpendiculars (in meters)
DWT = 8000; # ship's deadweight (in tons)

#Additional plot flags:
plot_nodes=1 #Yes=1 ; No=0
plot_waves=1 #Yes=1 ; No=0
plot_routes=1 #Yes=1 ; No=0

# END OF USER INPUTS   #######################