#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Safety_restrictions.py
SIMROUTE 2026 compatible

Detects:
 - Parametric Rolling
 - Surfriding / Bow Tripping
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from func_postprocess import rumIni, rumEnd, ang_encounter


# ---------------- USER INPUTS ----------------

trip_id = "TripID_1406"

offset = 0.2

plot_pr = 1
plot_sr = 1

# ---------------------------------------------


npz_path = f"../out/{trip_id}/{trip_id}.npz"

if not os.path.exists(npz_path):
    print("Simulation not found:", npz_path)
    raise SystemExit

print("Loading:", npz_path)

dat = np.load(npz_path, allow_pickle=True)


# ---------------------------------------------------
# NPZ STRUCTURE
# ---------------------------------------------------

meta = dat["arr_0"]

LonMin = meta[0]
LonMax = meta[1]
LatMin = meta[2]
LatMax = meta[3]

v0 = meta[4]

inc = meta[5]

nodIni = int(meta[6])
nodEnd = int(meta[7])

t_ini = int(meta[8])
time_res = int(meta[9])
WEN_form = int(meta[10])

Lbp = meta[11]
DWT = meta[12]

hs = dat["arr_1"]
fp = dat["arr_2"]

L_TripFix = dat["arr_3"]
L_Trip = dat["arr_4"]

L_CostTrip = dat["arr_5"]
L_ConsCostTrip = dat["arr_6"]


# ---------------------------------------------------

print("HS shape:", hs.shape)
print("FP shape:", fp.shape)
print("Route nodes:", len(L_Trip))


# ---------------------------------------------------
# BUILD MESH
# ---------------------------------------------------

inc_deg = inc / 60.0

Nx = int(np.floor((LonMax - LonMin) / inc_deg) + 2)
Ny = int(np.floor((LatMax - LatMin) / inc_deg) + 2)

tira_lon = [LonMin + i * inc_deg for i in range(Nx)]
tira_lat = [LatMin + j * inc_deg for j in range(Ny)]

nodes = np.zeros((Nx * Ny, 2))

for j in range(Ny):
    for i in range(Nx):
        nodes[Nx * j + i, 0] = tira_lon[i]
        nodes[Nx * j + i, 1] = tira_lat[j]

print("Mesh Re-built:", nodes.shape)


# ---------------------------------------------------
# PARAMETERS
# ---------------------------------------------------

Tr = 20
epsi = 0.1

L_sr_bt = []
L_pr = []


# ---------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------

for i in range(len(L_Trip) - 1):

    Ni = int(L_Trip[i])
    Ne = int(L_Trip[i + 1])

    if Ni >= nodes.shape[0] or Ne >= nodes.shape[0]:
        continue

    loni, lati = nodes[Ni]
    lone, late = nodes[Ne]

    for k in range(2):

        idx = i + k

        # ---- FIX for IndexError ----
        if idx >= len(L_CostTrip):
            continue

        cost_val = L_CostTrip[idx]

        if time_res == 1:

            ti = int(np.rint(cost_val))

        else:

            a, b = np.divmod(cost_val, time_res)

            if b > time_res / 2:
                ti = int(a + 1)
            else:
                ti = int(a)

        node = Ni if k == 0 else Ne

        if node >= hs.shape[0] or ti >= hs.shape[1]:
            continue

        hi = hs[node, ti]
        fpi = fp[node, ti]

        if np.isnan(hi) or np.isnan(fpi):
            continue

        diri = fpi

        rumb = rumIni(loni, lati, lone, late) if k == 0 else rumEnd(
            loni, lati, lone, late
        )

        angEnc = ang_encounter(rumb, diri)

        v = 1.8 * np.sqrt(Lbp) / np.cos(np.deg2rad(180 - angEnc))

        print(
            f"DEBUG node={node} time={ti} angEnc={angEnc:.2f} v={v:.2f} v0={v0:.2f}"
        )

        # ---------------------------------------------------
        # SURFRIDING
        # ---------------------------------------------------

        if 145 < angEnc < 225 and v0 > v:

            print("SURFRIDING at node:", node)

            L_sr_bt.append(node)

        # ---------------------------------------------------
        # PARAMETRIC ROLLING
        # ---------------------------------------------------

        Tw = fpi

        Te = 3 * Tw * Tw / (3 * Tw + v0 * np.cos(np.deg2rad(angEnc)))

        if abs(Te - Tr) < epsi * Tr or abs(2 * Te - Tr) < epsi * Tr:

            print("PARAMETRIC ROLLING at node:", node)

            L_pr.append(node)


# ---------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------

L_pr = np.unique(L_pr)
L_sr_bt = np.unique(L_sr_bt)

print("PR nodes:", len(L_pr))
print("SR nodes:", len(L_sr_bt))


# ---------------------------------------------------
# PLOT
# ---------------------------------------------------

LamC = ccrs.LambertConformal(
    central_longitude=(LonMin + LonMax) / 2,
    central_latitude=(LatMin + LatMax) / 2,
)

geo = ccrs.Geodetic()

extent = [
    LonMin - offset,
    LonMax + offset,
    LatMin - offset,
    LatMax + offset,
]

fig = plt.figure(figsize=(12, 6))

ax = plt.subplot(1, 1, 1, projection=LamC)


# ROUTE

lon = nodes[L_Trip[:-1], 0]
lat = nodes[L_Trip[:-1], 1]

ax.plot(lon, lat, "m", transform=geo, label="Optimized route")


# START / END

ax.plot(
    [nodes[nodIni, 0]],
    [nodes[nodIni, 1]],
    "^b",
    transform=geo,
    label="Departure",
)

ax.plot(
    [nodes[nodEnd, 0]],
    [nodes[nodEnd, 1]],
    "^r",
    transform=geo,
    label="Arrival",
)


# PARAMETRIC ROLLING

if plot_pr and len(L_pr) > 0:

    ax.plot(
        nodes[L_pr, 0],
        nodes[L_pr, 1],
        "oy",
        transform=geo,
        label="Param. rolling",
    )


# SURFRIDING

if plot_sr and len(L_sr_bt) > 0:

    ax.plot(
        nodes[L_sr_bt, 0],
        nodes[L_sr_bt, 1],
        "og",
        transform=geo,
        label="Surfriding",
    )


ax.set_extent(extent)

ax.coastlines(resolution="10m")

ax.add_feature(cfeature.LAND)

ax.gridlines(draw_labels=True)

ax.legend(loc="best")


# ---------------------------------------------------
# SAVE
# ---------------------------------------------------

out_file = f"../out/{trip_id}/Unstable_motions_{trip_id}.png"

plt.savefig(out_file, dpi=300)

print("Saved:", out_file)

plt.show()