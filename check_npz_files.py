import numpy as np
import os

file_path = './out/PALMA_BARNA_2.npz'

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