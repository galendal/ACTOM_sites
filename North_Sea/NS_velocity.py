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
from scipy import spatial

#%%
def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd;

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def parse_dms(dms):
    parts = re.split('[^\d\w]+', dms)
    lat = dms2dd(parts[0], parts[1], parts[2], parts[3])
    lng = dms2dd(parts[4], parts[5], parts[6], parts[7])

    return (lat, lng)

def find_nearest(xd, pos=[60.645556,3.726389]): # Default to Troll
    abslat = np.abs(xd.lat-pos[0])
    abslon = np.abs(xd.lon-pos[1])
    c = np.maximum(abslat, abslon)
    ([xloc], [yloc]) = np.where(c == np.min(c))
    return [xloc,yloc]


#%%
troll_lat=60.645556
troll_lon=3.726389
latspan=1
lonspan=0.5


# %%
def read_one(filenm, ):
    xd= xr.open_dataset('https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/NorKyst-800m_ZDEPTHS_his.an.2018120500.nc')
    xd.close()

#%%
xd= xr.open_dataset('https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/NorKyst-800m_ZDEPTHS_his.an.2018120500.nc')

tmp=xd[['h','u_eastward','v_northward']]
tmp
xd.close()
#%%
min_lon=troll_lon-lonspan
max_lon=troll_lon+lonspan

min_lat=troll_lat-latspan
max_lat=troll_lat+latspan

# %%
mask_lon = (xd.lon >= min_lon) & (xd.lon <= max_lon)
mask_lat = (xd.lat >= min_lat) & (xd.lat <= max_lat)

#%%
cropped_xd = xd.where(mask_lon & mask_lat, drop=True)
# %%

cropped_tmp = tmp.where(mask_lon & mask_lat, drop=True)
cropped_tmp.h.plot.contourf(x='lon',y='lat')