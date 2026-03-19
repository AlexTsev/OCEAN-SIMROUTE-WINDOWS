# Personal SIMROUTE Test Project

This is a personal adaptation of SIMROUTE (UPC-BarcelonaTech, Manel Grifoll). 
Used for learning, testing, and portfolio purposes. No private credentials are included.

################################################################################################

Running Trips Experiments in SimRoute Mini Project

The results of each trip experiment are printed in its corresponding TripID folder inside the out folder in source. These experiments can be altered using the parameter files for each trip:

Each trip has a parameter file named:
params_TripID_....py in the source folder.

Step 0: Determine Start and End Nodes (NEW)

Before running a simulation, use `find_ports.py` to compute the correct initial and final node indices from the given coordinates.

Run:

Step 1: Select the Trip to Run

Open SimRoute.py.

Change the boolean TripID_bool to True for the trip you want to run (set others to False).

Set TripID = <number> to the ID of the trip you want to run.

Remove the comment from the demo simulation you want to execute (e.g., HAKO_KAGO).

Step 2: Set Up Wave Data

Open get_waves_CMEMS.py in the source folder.

Make sure you have a Copernicus account.

Choose the dataset you want to download – this is controlled by the prod = parameter at the top of the corresponding params_TripID_....py file.

If you want the Global Ocean Waves Analysis and Forecast dataset specifically:

In get_waves_CMEMS.py, comment out the global prod line for other datasets and uncomment:

ID_DTSET='cmems_mod_glo_wav_anfc_0.083deg_PT3H-i'

Comment back the line for the 0.2° dataset if not needed.

Step 3: Generate Wave Files

Run make_waves.py in the source folder. This will generate the necessary wave files for your trip simulations.

Step 4: Run the Main Simulation

Run main.py.

Once completed, all results and logs will be stored in the out folder inside each TripID folder.