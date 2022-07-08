#%%
from netCDF4 import Dataset,num2date 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import time
import xarray as xr
import utm
import openpyxl
import pandas as pd
import json
import re
#%%
d = Dataset('https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/NorKyst-800m_ZDEPTHS_his.an.2018120500.nc')
print(d.variables['depth'][3:7])
# %%
# %%
troll_lat=60.645556
troll_lon=3.726389
# %%
lat=d.variables['lat'][:].data
lon=d.variables['lon'][:].data
# %%
abslat=np.abs(lat-troll_lat)
abslon=np.abs(lon-troll_lon)
latlonidx = np.unravel_index(np.argmin(np.maximum(abslon,abslat)),lat.shape)
# %%
latspan=5
lonspan=4

# %%
ue=d.variables['u_eastward'][:,:,latlonidx[0]-latspan:latlonidx[0]+latspan,latlonidx[1]-lonspan:latlonidx[1]+lonspan].data
# %%
d.variables['u_eastward']
# %%
xd= xr.open_dataset('https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/NorKyst-800m_ZDEPTHS_his.an.2018120500.nc')
# %%
dd=Dataset('https://thredds.met.no/thredds/dodsC/sea/norkyst800mv0_24h/NorKyst-800m_ZDEPTHS_avg.fc.2019022612.nc')
# %%
tmp=utm.to_latlon(554834.84, 6707818.42, 31,'V')
# %%
def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

# %%
wb = openpyxl.load_workbook(filename = '/Users/guttorm/Dropbox/Projects/ACTOM/Coding/Data/Norwegian site/Export.xlsx')
ws = wb['Wellbores, all']

from itertools import islice
data = ws.values
cols = next(data)[1:]
data = list(data)
idx = [r[0] for r in data]
data = (islice(r, 1, None) for r in data)
df = pd.DataFrame(data, index=idx, columns=cols)

#%%
df.set_index(df['OBJECTID'],inplace=True)
cols=['NS UTM [m]','EW UTM [m]','NS degrees','NS minutes','NS seconds','Water depth [m]','Well name']
wells=df[cols].to_xarray()





# JUnk 
# %%
wb['Wellbores, all'].values
# %%
from itertools import islice
data = ws.values
cols = next(data)[1:]
data = list(data)
idx = [r[0] for r in data]
data = (islice(r, 1, None) for r in data)
df = pd.DataFrame(data, index=idx, columns=cols)
# %%

# %%

def create_well(str):
    tmp=re.split(', |:',str)
    X=np.float(tmp[1])
    Y=np.float(tmp[3])
    latlon=utm.to_latlon(X, Y, 31,'V')
    print(X,Y)
    print(latlon)
    out=xr.Dataset(data_vars={
        "X":(np.float(X)),
        "Y":(np.float(Y)),
        "lat":(latlon[0]),
        "lon":(latlon[1])}
    )
    return out

# %%
wells=[]
for id in df.index:
    wells.append(create_well(id))
wells=xr.concat(wells, dim='wells')

# %%
