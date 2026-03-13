
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 23:10:59 2020
Code part of SIMROUTE (UPC-BarcelonaTech)
version 31/01/2021
@author: manel grifoll (UPC-BarcelonaTech)
"""

#from func_simroute import *
#from  params_IBI import *
from simroute import *
import matplotlib.pyplot as plt
import numpy as np
import sys
#from mpl_toolkits.basemap import Basemap

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os

tic()
mxcost=0
mxdks=0
if np.isnan(hs[nodIni,0]):
    print('The nodIni is land')
    sys.exit()

if np.isnan(hs[nodEnd,1]):
    print('The nodEnd is land')
    sys.exit()

flag= testVrtx(nodIni)
if flag is  False:
    print('The nodIni is in vertex move!')
    sys.exit()

flag= testVrtx(nodEnd)
if flag is  False:
    print('The nodEnd is in vertex move!')
    sys.exit()


'''   setled=np.zeros(shape=(Ny*Nx,4))
       settled each row gives information about the node corresponding to
       n. of row
       the variable is initialized to zero
       col 0  =  if there is a 1, it means that the node is closed
       col 1 the second column gives the cost at which it has closed
       col 2   the third column is the father node, 
       col 3  for the evaluation function
       min_c=np.ones(shape=(Nx*Ny,3))*np.inf
       min_c each row keeps information about the nodes, initialized at Inf
       col 0   the cost of the open node, because when a node is closed, it is 
           put at inf 
       col 1   is the father (when the node is closed, it is left at inf)
       col 2   for the evaluation function
       here the algorithm searches the optimum route at constant speed V0 , 
       en dos casos,1 ,sense  tenin present el onatge 
       i 0 , tenin present onatge
             
 '''
 ##
''' 
Let's first
do two different cases i=0 ,i=1
i=0 Case where the speed of the ship is altered by
the length and direction of the wave i=1 The speed of the ship is constant v0
'''
Ldebug=[]
print('Working very hard....!')
for i in range(2):
    setled=np.zeros(shape=(Ny*Nx,4))
    min_c=np.ones(shape=(Nx*Ny,3))*np.inf
    pidx=nodIni
    min_c[pidx,0]=0
    min_c[pidx,2]=np.nan
    if i==0:
        print('Init trip with waves')
    else:
        print('Init trip without waves')
    '''
        pidx node to close, the first time it is the initial one, 
        it will finish when it closes the end
    '''
    while (pidx != nodEnd) :
        setled[pidx,0]=1   # it closes the node to expland
        setled[pidx,1]=min_c[pidx,0];
        setled[pidx,2]=min_c[pidx,1];
#        print('pidx =  {}  {} {}\n'.format( pidx,i,i))
        min_c[pidx,2]=np.inf   # it is inutilized to min
        min_c[pidx,0]=np.inf
        neighbor_ids=veins(pidx)   # expanding list of neighbors
        for cidx in neighbor_ids:
            if setled[cidx,0]==0:   # if node is open, it works; if it is closed, nothing is done
                if (not np.isnan(hs[cidx,1])):
                    if i==0:
                        g=time_edge(v0,pidx,cidx,setled[pidx,1])    # accumulated time to pass the edge
                        if mxcost<setled[pidx,1] :
                            mxcost=setled[pidx,1]
                            print("Max. sailing time (in hours) = ",mxcost)
                    else:
                        g=dist_nods(pidx,cidx)/v0+setled[pidx,1]
                        if mxdks<setled[pidx,1] :
                            mxdks=setled[pidx,1]
                            print("Max. sailing time without waves (in hours) = ",mxdks)

                    heu=dist_nods(cidx,nodEnd)/v0   # heuristic time from the node to the end node
                    if (heu+g)<min_c[cidx,2]:
                            min_c[cidx,0]=g
                            min_c[cidx,1]=pidx
                            min_c[cidx,2]=heu+g

        pidx=int(np.where(min_c[:,2]==np.nanmin(min_c[:,2]))[0][0])

        if pidx==nodEnd:
            setled[pidx,0]=1
            setled[pidx,1]=min_c[pidx,0]
            setled[pidx,2]=min_c[pidx,1]

        #print('node: ',pidx)

    #'Finished, reconstructs the path from settled'while nod_p ~=nod_ini
    L_t=[]
    L_c=[]   # LLista amb els costos columna 1 del setled
    nod_p =nodEnd
    ''' we start with the last node and look at the parents of each node 
        until we reach the Ini node
    '''
    L_t.append(nodEnd)
    L_c.append(setled[nodEnd,1])
    while (nod_p != nodIni) :
        nod=int(setled[int(nod_p),2])
        cos=setled[int(nod),1]
        L_t.append(nod)
        L_c.append(cos)
        nod_p=nod
    if i==0:
        L_Trip=L_t[::-1]
        Cost_Opt=L_c[::-1]
        CostWave=setled[nodEnd,1]
    else:
        L_TripFix=L_t[::-1]
        CostConst=setled[nodEnd,1]
        L_ConsCostTrip=L_c[::-1]

#Calcul de les milles fetes
n=len(L_Trip)
distWave=0
for i in range(n-1):
    distWave=distWave+dist_nods(L_Trip[i],L_Trip[i+1])
n=len(L_TripFix)
distConst=0
for i in range(n-1):
    distConst=distConst+dist_nods(L_TripFix[i],L_TripFix[i+1])
''' Third part of the simulation:
We consider that a ship goes along the route that we have called constant
but take into account the speed if it is affected by the waves
We will call it the ctw route
'''
CostCtw=0
Cost_Min=[]
Cost_Min.append(CostCtw)
for i in range(len(L_TripFix)-1):
    CostCtw=time_edge(v0,L_TripFix[i],L_TripFix[i+1],CostCtw)
    Cost_Min.append(CostCtw)

#dat=np.load(lcd_out)
#ldc=dat['arr_0']
#grabarem les sortides

#output_dir = os.path.join(" 'out/'+name_Simu+'/plots' ", name_Simu)
# Αντικατάστησε το παραπάνω με αυτό:
report_dir = os.path.join("out", name_Simu)  # δημιουργεί τον φάκελο out/SimuName
os.makedirs(report_dir, exist_ok=True)

# Δημιουργία του αρχείου
report = os.path.join(report_dir, name_Simu + '_Res.txt')
frep=open(report,'w')
st='              SIMROUTE report:     '+name_Simu+'\n'
frep.write(st)
st='=========================================================================\n\n'
frep.write(st)
st= 'Initial Velocity in knots = {} \n'.format(v0)
frep.write(st)
print(st)
st='WEN_form = {:d} \n'.format(WEN_form)
print(st)
frep.write(st)

st='Departure:  Node = {:6d}  --  coordinates  ({:6.4f},{:6.4f})\n'
frep.write(st.format(nodIni,nodes[nodIni,0],nodes[nodIni,1]))
print(st.format(nodIni,nodes[nodIni,0],nodes[nodIni,1]))
# s=ARX[0]
# k=s.find('_',s.find('_')+1)
# Syear=s[k+1:k+5]
# Smon=s[k+5:k+7]
# Sdia=s[k+7:k+9]
Syear=str(date_Ini[0])
Smon=str(date_Ini[1])
Sdia=str(date_Ini[2])
Shora=str(t_ini)
dat=Sdia+'-'+Smon+'-'+Syear+' '+Shora+':00'
st='Departure time (day-month-year hour:min): '+dat+'\n'
#del k , s , Syear, Sdia, Shora, Smon
frep.write(st)
print(st)

#ARX=ferNoms(date_Ini, date_End, name_Simu)
st='Arrival:     Node = {:6d}  --  coordinates  ({:6.4f},{:6.4f})\n'
frep.write(st.format(nodEnd,nodes[nodEnd,0],nodes[nodEnd,1]))
print(st.format(nodEnd,nodes[nodEnd,0],nodes[nodEnd,1]))
st='Number of nodes: Nx={:6d}   Ny={:6d}   Nx*Ny={:6d}   \n'
print(st.format(Nx,Ny,Nx*Ny))
frep.write(st.format(Nx,Ny,Nx*Ny))
st='Geodetic Distance (in milles): {:6.2f}\n '
frep.write(st.format(dist_nods(nodIni,nodEnd)))
st='\n========================================================================\n'
frep.write(st)
print(st)
st='                                        Sailed hours    Sailed milles\n'
frep.write(st)
print(st)
st='Route Optimized:                          {:6.2f}            {:6.2f}    \n'
frep.write(st.format(Cost_Opt[-1],distWave))
print(st.format(Cost_Opt[-1],distWave))
st='Route Minimum Distance:                  {:6.2f}            {:6.2f}    \n'
print(st.format(Cost_Min[-1],distConst))
frep.write(st.format(Cost_Min[-1],distConst))
st='Route Minimum Distance (without waves):   {:6.2f}            {:6.2f}    \n'
print(st.format(CostConst,distConst))
frep.write(st.format(CostConst,distConst))
st='\n========================================================================\n\n'
'''  now we record results we put as name

'''
print('-------------- SIMROUTE DONE ---------------------')
print('-------------- Saving results in 3 files...')
print ('File simulation results created: ' + report )

prs = np.array([LonMin,LonMax,LatMin,LatMax,v0,inc,nodIni,nodEnd,t_ini,
                time_res,WEN_form,Lbp,DWT])
np.savez_compressed('out/'+name_Simu+'/'+name_Simu,prs,hs,dir,L_Trip,L_TripFix,
                    Cost_Opt,L_ConsCostTrip,Cost_Min,arxW())
######################
frep.write(st)
frep.close()
print ('File .npz results created: ' + 'out/'+name_Simu+'.npz')


nom_reco=name_Simu+'_MetaData.txt'
reco=open('out/'+name_Simu+'/'+nom_reco,'w')
st='name_Simu = \''+name_Simu+'\'\n'
reco.write(st)
st='LonMin = {:6.3f} \n'
reco.write(st.format(LonMin))
st='LonMax = {:6.3f} \n'
reco.write(st.format(LonMax))
st='LatMin = {:6.3f} \n'
reco.write(st.format(LatMin))
st='LatMax = {:6.3f} \n'
reco.write(st.format(LatMax))
st='inc = {:6.3f} \n'
reco.write(st.format(inc))
st='nodIni = {:d} \n'
reco.write(st.format(nodIni))
st='nodEnd = {:d} \n'
reco.write(st.format(nodEnd))
reco.write(arxW()+'\n')
#reco.write('dir_arx = \'storeWaves/\'\n')
st='time_res = {:d} \n'
reco.write(st.format(time_res))
st='t_ini = {:d} \n'
reco.write(st.format(t_ini))
st='v0 = {:6.3f} \n'
reco.write(st.format(v0))
st='WEN_form = {:d} \n'
reco.write(st.format(WEN_form))
st='Lbp = {:d} \n'
reco.write(st.format(int(Lbp)))
st='DWT = {:d} \n'
reco.write(st.format(int(DWT)))
reco.close()
print ('File simulation metadata created: ' + nom_reco)

report='out/'+name_Simu+'/'+name_Simu+'_Route.txt'
frout=open(report,'w')
st='  nnod     Lon    Lat      Cost    hs      dir   \n'
frout.write(st)
for i in range(len(L_Trip)):
    n=L_Trip[i]
    lonn=nodes[n,0]
    latt=nodes[n,1]
    if time_res==3:
        ccost= Cost_Opt[i]/3
    else:
        ccost=Cost_Opt[i]
    hh=hs[n,int(np.round(ccost))]
    dirr=dir[n,int(np.round(ccost))]
    st='{:7d} {:8.3f} {:7.3f} {:7.3f} {:5.2f} {:6.2f} \n'.format(n,lonn,latt,ccost,hh,dirr)
    frout.write(st)
frout.close()


print ('File simulation rout created')
toc()
# -------------------- Standard 2D plot --------------------
if plot_routes == 1:

    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    # =====================================================
    # Helper function
    # =====================================================
    def distL(cost_vector, t):
        idx = 0
        while idx < len(cost_vector) and cost_vector[idx] <= t:
            idx += 1
        return idx

    # =====================================================
    # Rebuild grid (same mesh as simulation)
    # =====================================================
    inc_deg = inc / 60.0
    Nx = int(np.floor((LonMax - LonMin) / inc_deg) + 2)
    Ny = int(np.floor((LatMax - LatMin) / inc_deg) + 2)

    tira_lon = [LonMin + i*inc_deg for i in range(Nx)]
    tira_lat = [LatMin + j*inc_deg for j in range(Ny)]

    nodes_mesh = np.zeros((Nx*Ny,2))
    for j in range(Ny):
        for i in range(Nx):
            nodes_mesh[Nx*j+i,0] = tira_lon[i]
            nodes_mesh[Nx*j+i,1] = tira_lat[j]

    Xnod, Ynod = np.meshgrid(tira_lon, tira_lat)
    vmax_hs = np.nanmax(hs)

    # =====================================================
    # Create output directory for simulation
    # =====================================================
    output_dir = os.path.join(report_dir + '/plots')
    os.makedirs(output_dir, exist_ok=True)

    # =====================================================
    # 1️⃣ STANDARD 2D MAP
    # =====================================================
    t_plot = 6
    hs_rec = hs[:, t_plot].reshape((Ny,Nx))

    fig, ax = plt.subplots(figsize=(10,8))
    im = ax.pcolor(Xnod, Ynod, hs_rec, cmap="viridis", vmin=0, vmax=vmax_hs)
    plt.colorbar(im, ax=ax, label="Wave height [m]")

    ax.plot(nodes_mesh[L_TripFix,0], nodes_mesh[L_TripFix,1],"orange", linewidth=2, label="Minimum Distance")
    ax.plot(nodes_mesh[L_Trip,0], nodes_mesh[L_Trip,1], "m", linewidth=2, label="Optimized Route")
    ax.scatter(nodes_mesh[nodIni,0], nodes_mesh[nodIni,1], color="blue", marker="^", s=120, label="Departure")
    ax.scatter(nodes_mesh[nodEnd,0], nodes_mesh[nodEnd,1], color="red", marker="X", s=120, label="Arrival")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(name_Simu + " - Standard 2D Wave Map")
    ax.legend(loc="best")
    #print('EIKONA')
    standard_map_file = os.path.join(output_dir, name_Simu + "_Standard2DMap.png")
    fig.savefig(standard_map_file, dpi=300)
    plt.show()
    plt.close(fig)

    # =====================================================
    # 2️⃣ ROUTE + WAVES ANIMATION FRAMES
    # =====================================================
    print("Creating route-wave frames...")

    nred = 10  # arrows plotted every 10 grid points
    sc = 60    # scale factor for arrow length
    wd_quiver = 0.002  # arrow width
    inc_frame = 1

    hsmax = np.nanmax(hs)
    nmax = Cost_Min[-1]
    n_frames = np.int_(np.arange(0, nmax, inc_frame))
    frame_list = n_frames.tolist()
    frame_list.append(int(np.ceil(nmax)))

    print("Frames to create:", len(frame_list))
    k = 0

    for t in frame_list:

        if time_res == 1:
            hs_rec = hs[:,int(t)].reshape((Ny,Nx))
            dir_rec = dir[:,int(t)].reshape((Ny,Nx)) + 180
        else:
            idx = int(np.round(t/3))
            hs_rec = hs[:,idx].reshape((Ny,Nx))
            dir_rec = dir[:,idx].reshape((Ny,Nx)) + 180

        U = hs_rec*np.sin(np.deg2rad(dir_rec))
        V = hs_rec*np.cos(np.deg2rad(dir_rec))

        tl = distL(Cost_Opt, t) if t < Cost_Opt[-1] else len(Cost_Opt)
        tc = distL(Cost_Min, t) if t < Cost_Min[-1] else len(Cost_Min)

        lon_opt = nodes_mesh[L_Trip[0:tl],0]
        lat_opt = nodes_mesh[L_Trip[0:tl],1]
        lon_min = nodes_mesh[L_TripFix[0:tc],0]
        lat_min = nodes_mesh[L_TripFix[0:tc],1]

        fig, ax = plt.subplots(figsize=(10,10))
        im = ax.pcolor(Xnod, Ynod, hs_rec, vmin=0, vmax=hsmax)
        ax.plot(lon_min, lat_min, "orange", label="Minimum distance route")
        ax.plot(lon_opt, lat_opt, "m", label="Optimized route")
        ax.scatter(nodes_mesh[nodIni,0], nodes_mesh[nodIni,1], color="blue", marker="^", s=120, label="Departure")
        ax.scatter(nodes_mesh[nodEnd,0], nodes_mesh[nodEnd,1], color="red", marker="X", s=120, label="Arrival")
        ax.quiver(Xnod[::nred,::nred], Ynod[::nred,::nred], U[::nred,::nred], V[::nred,::nred], scale=sc, width=wd_quiver)
        ax.set_title(name_Simu + " time = {:.2f} hours".format(t))
        ax.legend(loc="best")
        plt.colorbar(im, ax=ax)

        fig_file = os.path.join(output_dir, f"{name_Simu}_frame_{k:03d}.png")
        fig.savefig(fig_file, dpi=400)
        plt.close(fig)
        k += 1

    print(f"All {k} frames created.")
    print("Generating Projected Maps... (this may take a few seconds)")

    # =====================================================
    # Show last animation frame
    # =====================================================
    last_t = frame_list[-1]
    if time_res == 1:
        hs_rec = hs[:, int(last_t)].reshape((Ny, Nx))
        dir_rec = dir[:, int(last_t)].reshape((Ny, Nx)) + 180
    else:
        idx = int(np.round(last_t / 3))
        hs_rec = hs[:, idx].reshape((Ny, Nx))
        dir_rec = dir[:, idx].reshape((Ny, Nx)) + 180

    U = hs_rec * np.sin(np.deg2rad(dir_rec))
    V = hs_rec * np.cos(np.deg2rad(dir_rec))

    tl = distL(Cost_Opt, last_t) if last_t < Cost_Opt[-1] else len(Cost_Opt)
    tc = distL(Cost_Min, last_t) if last_t < Cost_Min[-1] else len(Cost_Min)

    lon_opt = nodes_mesh[L_Trip[0:tl], 0]
    lat_opt = nodes_mesh[L_Trip[0:tl], 1]
    lon_min = nodes_mesh[L_TripFix[0:tc], 0]
    lat_min = nodes_mesh[L_TripFix[0:tc], 1]

    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.pcolor(Xnod, Ynod, hs_rec, vmin=0, vmax=hsmax)
    ax.plot(lon_min, lat_min, "orange", label="Minimum distance route")
    ax.plot(lon_opt, lat_opt, "m", label="Optimized route")
    ax.scatter(nodes_mesh[nodIni, 0], nodes_mesh[nodIni, 1], color="blue", marker="^", s=120, label="Departure")
    ax.scatter(nodes_mesh[nodEnd, 0], nodes_mesh[nodEnd, 1], color="red", marker="X", s=120, label="Arrival")
    ax.quiver(Xnod[::nred, ::nred], Ynod[::nred, ::nred], U[::nred, ::nred], V[::nred, ::nred], scale=sc, width=wd_quiver)
    ax.set_title(name_Simu + " - Last Frame (t={:.2f} hours)".format(last_t))
    ax.legend(loc="best")
    plt.colorbar(im, ax=ax)
    plt.show()
    plt.close(fig)


    # =====================================================
    # 3️⃣ PROJECTED MAPS (Plate-Carree + Lambert)
    # =====================================================
    offset = 0.2
    pc = ccrs.PlateCarree()
    lambert = ccrs.LambertConformal(
        central_longitude=(LonMin+LonMax)/2,
        central_latitude=(LatMin+LatMax)/2
    )
    geo = ccrs.Geodetic()
    extent = [LonMin-offset, LonMax+offset, LatMin-offset, LatMax+offset]

    fig = plt.figure(figsize=(20,10))

    # Plate-Carree
    ax_pc = plt.subplot(1,2,1, projection=pc)
    im_pc = ax_pc.pcolor(Xnod, Ynod, hs_rec, vmin=0, vmax=vmax_hs, cmap='viridis', transform=pc)
    plt.colorbar(im_pc, ax=ax_pc, label='Wave height [m]')
    ax_pc.set_extent(extent)
    ax_pc.add_feature(cfeature.LAND)
    ax_pc.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax_pc.coastlines(resolution='10m')
    ax_pc.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    ax_pc.plot(lon_min, lat_min, 'orange', transform=pc, label='Minimum Distance')
    ax_pc.plot(lon_opt, lat_opt, 'm', transform=pc, label='Optimized')
    ax_pc.plot(nodes_mesh[nodIni,0], nodes_mesh[nodIni,1], '^', color="blue", transform=pc, label='Departure')
    ax_pc.plot(nodes_mesh[nodEnd,0], nodes_mesh[nodEnd,1], 'X', color="red", transform=pc, label='Arrival')
    ax_pc.quiver(Xnod[::nred, ::nred], Ynod[::nred, ::nred], U[::nred, ::nred], V[::nred, ::nred], scale=sc, width=wd_quiver, pivot='middle', transform=pc)
    ax_pc.legend(loc="best")
    ax_pc.set_title(f'{name_Simu} (Plate-Carree) - t={last_t}h')

    # Lambert
    ax_lam = plt.subplot(1,2,2, projection=lambert)
    im_lam = ax_lam.pcolor(Xnod, Ynod, hs_rec, vmin=0, vmax=vmax_hs, cmap='viridis', transform=pc)
    plt.colorbar(im_lam, ax=ax_lam, label='Wave height [m]')
    ax_lam.set_extent(extent, crs=pc)
    ax_lam.add_feature(cfeature.LAND)
    ax_lam.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax_lam.coastlines(resolution='10m')
    ax_lam.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    ax_lam.plot(lon_min, lat_min, 'orange', transform=geo)
    ax_lam.plot(lon_opt, lat_opt, 'm', transform=geo)
    ax_lam.plot(nodes_mesh[nodIni,0], nodes_mesh[nodIni,1], '^', color="blue", transform=geo)
    ax_lam.plot(nodes_mesh[nodEnd,0], nodes_mesh[nodEnd,1], 'X', color="red", transform=geo)
    ax_lam.quiver(Xnod[::nred, ::nred], Ynod[::nred, ::nred], U[::nred, ::nred], V[::nred, ::nred], scale=sc+30, width=wd_quiver, pivot='middle', transform=pc)
    ax_lam.set_title(f'{name_Simu} (Lambert Conformal) - t={last_t}h')

    projected_file = os.path.join(output_dir, name_Simu + "_ProjectedMaps.png")
    fig.savefig(projected_file, dpi=300)
    plt.show()
    plt.close(fig)

    # =====================================================
    # 4️⃣ Ship Emissions
    # =====================================================