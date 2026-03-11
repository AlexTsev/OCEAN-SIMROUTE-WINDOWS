import xarray as xr
import os

folder = "./storeWaves"
print(os.listdir(folder))

# Αρχείο που κατέβασες από Copernicus
file_trip1 = "./storeWaves/Waves_TripID_1368_2022-04-26%2022-05-10.nc"
file_trip2 = "./storeWaves/Waves_TripID_1398_2023-04-06%2023-05-05.nc"
file_trip3 = "./storeWaves/Waves_MEDSEA_20200120.nc"

# Άνοιγμα αρχείου με xarray
ds1 = xr.open_dataset(file_trip1)
ds2 = xr.open_dataset(file_trip2)
ds3 = xr.open_dataset(file_trip3)

# Δες τα variables και dimensions
print("=== Trip 1368 ===")
print(ds1)
print("\nVariables available:", list(ds1.data_vars))

print("\n=== Trip 1398 ===")
print(ds2)
print("\nVariables available:", list(ds2.data_vars))

print("\n=== Trip Waves_MEDSEA ===")
print(ds3)
print("\nVariables available:", list(ds3.data_vars))


# Δες ένα sample των δεδομένων
print("\nSample wave height (VHM0) Trip 1368:")
print(ds1["VHM0"].isel(time=0))  # πρώτο timestamp

print("\nSample wave height (VHM0) Trip 1398:")
print(ds2["VHM0"].isel(time=0))

print("\nSample wave height (VHM0) Trip Waves_MEDSEA:")
print(ds3["VHM0"].isel(time=0))



print('\n')
import numpy as np

# Replace with your simulation name
name_Simu = 'HAKO_KAGO_2'

# Path to the intermediate NPZ
npz_file = f'in/{name_Simu}_wInt.npz'

# Load NPZ
data = np.load(npz_file, allow_pickle=True)

# List arrays inside
print(f"Loading NPZ file: {npz_file}")
print("Arrays in NPZ:")

for key in data.files:
    arr = data[key]
    print(f"  {key}: shape={arr.shape}, dtype={arr.dtype}")
    # Show a small sample for arrays with >0 size
    if arr.size > 0 and arr.size <= 20:
        print(f"    Sample: {arr}")
    elif arr.size > 20:
        print(f"    First 5 elements: {arr.ravel()[:5]}")