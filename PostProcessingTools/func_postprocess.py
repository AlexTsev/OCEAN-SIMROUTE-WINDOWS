#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for SIMROUTE postprocessing
Version upgraded for current libraries and np.ndarray support
"""

import numpy as np

def ang_encounter(ang_ship, ang_wave):
    """Compute relative angle between ship heading and wave direction."""
    theta = (ang_wave - ang_ship) % 360
    return theta

def dist_arc(loni, lati, lone, late):
    """
    Great-circle distance in radians between two points given in degrees
    using spherical law of cosines.
    """
    cosp = (np.cos(np.deg2rad(90 - lati)) * np.cos(np.deg2rad(90 - late)) +
            np.sin(np.deg2rad(90 - lati)) * np.sin(np.deg2rad(90 - late)) *
            np.cos(np.deg2rad(lone - loni)))
    return np.arccos(np.clip(cosp, -1, 1))  # clip to avoid numerical errors

def dist_mn(loni, lati, lone, late):
    """
    Distance in nautical miles between two points given in degrees.
    """
    d_rads = dist_arc(loni, lati, lone, late)
    d_nm = d_rads * 180 / np.pi * 60
    return d_nm

def rumIni(loni, lati, lone, late):
    """
    Initial bearing (degrees) from start to end point.
    """
    if lati == late:
        return 270 if loni > lone else 90
    loni = loni + 1e-8  # avoid division by zero
    k = dist_arc(loni, lati, lone, late)
    cosI = (np.cos(np.deg2rad(90 - late)) - np.cos(k) * np.cos(np.deg2rad(90 - lati))) / (
            np.sin(k) * np.sin(np.deg2rad(90 - lati)))
    I = np.arccos(np.clip(cosI, -1, 1)) * 180 / np.pi
    return (360 - I) if loni > lone else I

def rumEnd(loni, lati, lone, late):
    """
    Final bearing (degrees) from start to end point.
    """
    if lati == late:
        return 270 if loni > lone else 90
    loni = loni + 1e-8
    k = dist_arc(loni, lati, lone, late)
    cosE = (np.cos(np.deg2rad(90 - lati)) - np.cos(k) * np.cos(np.deg2rad(90 - late))) / (
            np.sin(k) * np.sin(np.deg2rad(90 - late)))
    E = np.arccos(np.clip(cosE, -1, 1)) * 180 / np.pi
    return (180 + E) if loni > lone else (180 - E)

def distL(Lst, m):
    """
    Given a sorted list Lst and a value m, return the index of the element
    closest to m.
    """
    Lst = np.asarray(Lst)
    idx = np.searchsorted(Lst, m)
    if idx == 0:
        return 0
    elif idx >= len(Lst):
        return len(Lst) - 1
    else:
        before = Lst[idx - 1]
        after = Lst[idx]
        return idx - 1 if (m - before) <= (after - m) else idx