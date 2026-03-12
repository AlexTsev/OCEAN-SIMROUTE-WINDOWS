#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ship emissions calculation for SIMROUTE (UPC-BarcelonaTech)
Updated for new .npz structure and NC wave file reference
@author: Updated for current environment
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from func_postprocess import dist_mn

# --------------------- USER SETTINGS ---------------------
name_Simu = 'TripID_1368'  # Name of the simulation/trip

# Engine and fuel parameters
toTn = 1 / 1e6       # Convert g → Tn
EL = 0.80            # Engine load %
Pow_Ins = 18000      # Engine power (kW)
V_design = 26        # Design speed (knots)
SFOC = 200           # g/kWh
SC = 0.005           # Sulfur content (%)
CC = 0.88            # Carbon content (%)
Engine_RPM = 500     # Engine rpm

# Molecular weights
M_S = 32.0655
M_SO2 = 64.06436
M_C = 12.01
M_CO2 = 44.0886

# Particulate matter
EF_EC = 0.08
EF_OC = 0.2
EF_ASH = 0.06
OC_EL = 1.024

# --------------------- FILES ---------------------
arx = f'../out/{name_Simu}/{name_Simu}.npz'
if not os.path.exists(arx):
    print(f'Simulation {arx} does not exist')
    raise SystemExit

arx_out = f'../out/{name_Simu}/Emissions_{name_Simu}.txt'

# --------------------- LOAD DATA ---------------------
dat = np.load(arx, allow_pickle=True)

# Metadata
meta = dat['arr_0'].astype(float)
LonMin, LonMax, LatMin, LatMax = meta[0], meta[1], meta[2], meta[3]
v0 = meta[4]
inc = meta[5] / 60.0  # convert to degrees?

# Trip nodes
L_Trip = dat['arr_3'].astype(int)
L_TripFix = dat['arr_4'].astype(int)

# Costs / times
Cost_Opt = dat['arr_5'].astype(float)
Cost_Min = dat['arr_6'].astype(float)
L_ConsCostTrip = dat['arr_7'].astype(float)

# Wave NC file reference
ARX = str(dat['arr_8'])

# --------------------- BUILD NODES ---------------------
Nx = int(np.floor((LonMax - LonMin) / inc) + 2)
Ny = int(np.floor((LatMax - LatMin) / inc) + 2)

tira_lon = [LonMin + i*inc for i in range(Nx)]
tira_lat = [LatMin + j*inc for j in range(Ny)]

nodes = np.zeros((Nx*Ny, 2))
for j in range(Ny):
    for i in range(Nx):
        nodes[Nx*j + i, 0] = tira_lon[i]
        nodes[Nx*j + i, 1] = tira_lat[j]

inc = inc * 60  # back to minutes?

# --------------------- SPEED CALCULATIONS ---------------------
nTrack = len(L_Trip) - 1
v_opt = np.zeros(nTrack)
for i in range(nTrack):
    N1, N2 = L_Trip[i], L_Trip[i+1]
    v_opt[i] = dist_mn(nodes[N1,0], nodes[N1,1],
                        nodes[N2,0], nodes[N2,1]) / (Cost_Opt[i+1]-Cost_Opt[i])

nTrack = len(L_TripFix) - 1
v_min = np.zeros(nTrack)
for i in range(nTrack):
    N1, N2 = L_TripFix[i], L_TripFix[i+1]
    v_min[i] = dist_mn(nodes[N1,0], nodes[N1,1],
                        nodes[N2,0], nodes[N2,1]) / (Cost_Min[i+1]-Cost_Min[i])

# --------------------- POWER CALCULATIONS ---------------------
cte_k = (EL * Pow_Ins) / (V_design ** 3)
Pow_trans_h = cte_k * (v_opt ** 3)
Pow_trans_h_min = cte_k * (v_min ** 3)

Pow_trans = Pow_trans_h.sum() / len(Pow_trans_h)
Pow_trans_min = Pow_trans_h_min.sum() / len(Pow_trans_h_min)

Delta_V = v0 - v_opt
Delta_V_min = v0 - v_min

Pow_Ef = Pow_Ins * 0.8
Delta_Pow = Pow_trans_h * (1. / ((1 - Delta_V/v0) ** 3) - 1)
Pow_New = Pow_Ef + Delta_Pow
EL_New = Pow_New / Pow_Ins
SFOC_REL_New = 0.445*(EL_New**2) - 0.71*EL_New + 1.28
SFOC_End = SFOC_REL_New * SFOC
Interv_t = np.diff(Cost_Opt)
Fuel_comp_New = Pow_New * SFOC_End * Interv_t
Fuel_comp_End = np.sum(Fuel_comp_New)

Delta_Pow_min = Pow_trans_h_min * (1. / ((1 - Delta_V_min/v0) ** 3) - 1)
Pow_New_min = Pow_Ef + Delta_Pow_min
EL_New_min = Pow_New_min / Pow_Ins
SFOC_REL_New_min = 0.445*(EL_New_min**2) - 0.71*EL_New_min + 1.28
SFOC_End_min = SFOC_REL_New_min * SFOC
Interv_t_min = np.diff(Cost_Min)
Fuel_comp_New_min = Pow_New_min * SFOC_End_min * Interv_t_min
Fuel_comp_End_min = np.sum(Fuel_comp_New_min)

Fuel_saving = (1 - (Fuel_comp_End / Fuel_comp_End_min)) * 100

# --------------------- EMISSIONS ---------------------
n_SO2_Interv = (SFOC_End * SC) / M_S
Emi_fac_SO2_Interv = M_SO2 * n_SO2_Interv
SO2_Interv = Pow_New * EL_New * Emi_fac_SO2_Interv * Interv_t
SO2_End = np.sum(SO2_Interv)

n_CO2_Interv = (SFOC_End * CC) / M_C
Emi_fac_CO2_Interv = M_CO2 * n_CO2_Interv
CO2_Interv = Pow_New * EL_New * Emi_fac_CO2_Interv * Interv_t
CO2_End = np.sum(CO2_Interv)

if Engine_RPM < 130:
    Emi_fac_NOx = 17
elif Engine_RPM <= 2000:
    Emi_fac_NOx = 45 * Engine_RPM ** (-0.2)
else:
    Emi_fac_NOx = 9.8
NOx_Interv = Pow_New * EL_New * Emi_fac_NOx * Interv_t
NOx_End = np.sum(NOx_Interv)

EF_SO4 = 0.312 * SC
EF_H2O = 0.244 * SC
Emi_fac_PM_Interv = SFOC_REL_New * (EF_SO4 + EF_H2O + EF_OC*OC_EL + EF_EC + EF_ASH)
PM_Interv = Pow_New * EL_New * Emi_fac_PM_Interv * Interv_t
PM_End = np.sum(PM_Interv)

# --------------------- MIN ROUTE EMISSIONS ---------------------
n_SO2_Interv_min = (SFOC_End_min * SC) / M_S
Emi_fac_SO2_Interv_min = M_SO2 * n_SO2_Interv_min
SO2_Interv_min = Pow_New_min * EL_New_min * Emi_fac_SO2_Interv_min * Interv_t_min
SO2_End_min = np.sum(SO2_Interv_min)

n_CO2_Interv_min = (SFOC_End_min * CC) / M_C
Emi_fac_CO2_Interv_min = M_CO2 * n_CO2_Interv_min
CO2_Interv_min = Pow_New_min * EL_New_min * Emi_fac_CO2_Interv_min * Interv_t_min
CO2_End_min = np.sum(CO2_Interv_min)

NOx_Interv_min = Pow_New_min * EL_New_min * Emi_fac_NOx * Interv_t_min
NOx_End_min = np.sum(NOx_Interv_min)

Emi_fac_PM_Interv_min = SFOC_REL_New_min * (EF_SO4 + EF_H2O + EF_OC*OC_EL + EF_EC + EF_ASH)
PM_Interv_min = Pow_New_min * EL_New_min * Emi_fac_PM_Interv_min * Interv_t_min
PM_End_min = np.sum(PM_Interv_min)

Emissions_mitigation_percentage = (1 - (CO2_End / CO2_End_min)) * 100

# --------------------- WRITE OUTPUT ---------------------
with open(arx_out, 'w') as emi:
    emi.write(f'Simulation name: {name_Simu}\n')
    emi.write(f'Fuel Consumption opt route: {Fuel_comp_End*toTn:10.3f} Tn\n')
    emi.write(f'Fuel Consumption minimum route: {Fuel_comp_End_min*toTn:10.3f} Tn\n')
    emi.write(f'Fuel consumption reduction following optimum route: {Fuel_saving:4.2f}%\n')
    emi.write(f'Percentage of emissions mitigation following optimum route: {Emissions_mitigation_percentage:.2f}%\n')
    emi.write(f'CO2 optimized: {CO2_End*toTn:7.3f} Tn\n')
    emi.write(f'CO2 minimum dist.: {CO2_End_min*toTn:7.3f} Tn\n')
    emi.write(f'SO2 optimized: {SO2_End*toTn:7.3f} Tn\n')
    emi.write(f'SO2 minimum dist.: {SO2_End_min*toTn:7.3f} Tn\n')
    emi.write(f'NOx optimized: {NOx_End*toTn:7.3f} Tn\n')
    emi.write(f'NOx minimum dist.: {NOx_End_min*toTn:7.3f} Tn\n')
    emi.write(f'PM optimized: {PM_End*toTn:7.3f} Tn\n')
    emi.write(f'PM minimum dist.: {PM_End_min*toTn:7.3f} Tn\n')

# --------------------- PLOTS ---------------------
fig, axs = plt.subplots(2,2, figsize=(9,9))
axs[0,0].plot(Cost_Opt[1:], np.cumsum(CO2_Interv*toTn), 'm', label='CO2 opt')
axs[0,0].plot(Cost_Min[1:], np.cumsum(CO2_Interv_min*toTn), 'orange', label='CO2 min')
axs[0,0].set_title('Accum. CO2')
axs[0,0].grid(True)
axs[0,0].legend(loc='upper left')

axs[0,1].plot(Cost_Opt[1:], np.cumsum(NOx_Interv*toTn), 'm', label='NOx opt')
axs[0,1].plot(Cost_Min[1:], np.cumsum(NOx_Interv_min*toTn), 'orange', label='NOx min')
axs[0,1].set_title('Accum. NOx')
axs[0,1].grid(True)
axs[0,1].legend(loc='upper left')

axs[1,0].plot(Cost_Opt[1:], np.cumsum(SO2_Interv*toTn), 'm', label='SO2 opt')
axs[1,0].plot(Cost_Min[1:], np.cumsum(SO2_Interv_min*toTn), 'orange', label='SO2 min')
axs[1,0].set_title('Accum. SO2')
axs[1,0].set_xlabel('Hours since departure')
axs[1,0].set_ylabel('Emissions (Tn)')
axs[1,0].grid(True)
axs[1,0].legend(loc='upper left')

axs[1,1].plot(Cost_Opt[1:], np.cumsum(PM_Interv*toTn), 'm', label='PM opt')
axs[1,1].plot(Cost_Min[1:], np.cumsum(PM_Interv_min*toTn), 'orange', label='PM min')
axs[1,1].set_title('Accum. PM')
axs[1,1].set_xlabel('Hours since departure')
axs[1,1].grid(True)
axs[1,1].legend(loc='upper left')

plt.tight_layout()
plt.savefig(f'../out/{name_Simu}/Emission_accumulated_{name_Simu}.png', dpi=300)
plt.show()