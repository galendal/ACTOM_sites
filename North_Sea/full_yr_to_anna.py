#%%
import NS_velocity
import numpy as np

#%%
year = 2021
month = 10
spanx=40
spany=40
lat=60.7736192761523
lon= 4.05334808493048
verbose=True

pos=[lat,lon]
span=[spanx,spany]
#%%
for month in np.arange(11,13):
    print(month)

#%%

for month in np.arange(11,13):
    NS_velocity.read_month(year= year, month=month, span=span, pos= pos, save=True, verbose=verbose)
# %%
