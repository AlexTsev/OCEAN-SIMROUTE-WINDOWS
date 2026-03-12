import numpy as np
import os

file_path2 = './in/TripID_1388_wInt.npz'
file_path = './out/TripID_1368.npz'

if os.path.exists(file_path) == False:
    print('Simulation '+file_path+' not exist')
    raise SystemExit

data = np.load(file_path)
print("Arrays in this file:", data.files)

for name in data.files:
    arr = data[name]
    print(f"{name}: shape = {arr.shape}, dtype = {arr.dtype}, sample = {arr.flatten()[:5]}")


for k in data.files:
    arr = data[k]
    print(k, arr.shape, arr.nbytes/1e6, "MB")


for key in data.files:
    print(key, type(data[key]), data[key].shape if hasattr(data[key], 'shape') else 'scalar', data[key].dtype)

#ΠΡΩΤΑ 10 ΣΤΟΙΧΕΙΑ

'\n ΠΡΩΤΑ 10 ΣΤΟΙΧΕΙA:'

# Arrays
hs = data['arr_1']
fp = data['arr_2']
dir_w = data['arr_3']
L_Trip = data['arr_4']
L_TripFix = data['arr_5']

print("=== First 10 elements ===")
print("L_Trip:", L_Trip[:10])
print("L_TripFix:", L_TripFix[:10])
print("dir_w:", dir_w[:10])
print("hs:", hs[:10])
print("fp:", fp[:10])

# Test mapping: see if any L_Trip values are bigger than dir_w indices
for i, node_idx in enumerate(L_Trip[:10]):
    if node_idx >= len(dir_w):
        print(f"L_Trip[{i}] = {node_idx} is out of bounds for dir_w (size {len(dir_w)})")
    else:
        print(f"L_Trip[{i}] = {node_idx} maps to dir_w[{node_idx}] = {dir_w[node_idx]}")

print("\nDone. You can now check how to map nodes to dir_w indices.")