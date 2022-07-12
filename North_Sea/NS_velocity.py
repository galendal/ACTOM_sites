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



def crop_depth(inxarr):
    return inxarr.isel(depth=(inxarr.depth<=inxarr.h).argmin(dim='depth')-1)

# def find_mask(inxarr, pos=np.array([60.645556,3.726389]), span=np.array([0.15,0.15])):
#     min_latlon=pos-span
#     max_latlon=pos+span
#     mask_lat = (inxarr.lat >= min_latlon[0]) & (inxarr.lat <= max_latlon[0])
#     mask_lon = (inxarr.lon >= min_latlon[1]) & (inxarr.lon <= max_latlon[1])
#     mask=mask_lon & mask_lat
#     return mask

# def cropped_data(inxarr, mask=None):
#     if not mask.any():
#         print('Maske empty, exiting')
#         out=[]
#     else:
#         cropped_out = inxarr.where(mask, drop=True)
#         out=cropped_out.isel(depth=(cropped_out.depth<=cropped_out.h).argmin(dim='depth')-1)
#     return out
    
def cropped_data(inxarr, pos=[60.645556,3.726389],span=[4,4]):
    ii,jj=find_nearest(inxarr, pos)
    out = inxarr.isel(X=np.arange(jj-span[0],jj+span[0]+1),Y=np.arange(ii-span[1],ii+span[1]+1))
    out=crop_depth(out)
    return out

def add_utm_coords(inxarr):
    easting,northing, zone, letter=utm.from_latlon(inxarr.lat.values,inxarr.lon.values)
    out=inxarr.copy()
    out=out.assign_coords(utm_E=(('Y','X'),easting))
    out=out.assign_coords(utm_N=(('Y','X'),easting))
    out.attrs['UTM zone']=zone
    out.attrs['UTM letter']=letter
    return out

def read_one(filenm,pos=np.array([60.645556,3.726389]), span=[4,4] ):
    xd= xr.open_dataset(filenm)
    
    tmp=xd[['h','u_eastward','v_northward']]
    
    cropped=cropped_data(tmp, pos, span)
    xd.close()
    return cropped

#%%
troll_lat=60.645556
troll_lon=3.726389
latspan=0.15
lonspan=0.15


# %%


#%%
xd = read_one('https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/NorKyst-800m_ZDEPTHS_his.an.2018120500.nc')

xd

#%%
filestem='https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/NorKyst-800m_ZDEPTHS_his.an.202205'
filetail='00.nc'
data=[]
for mnt in np.arange(2):
    filenm=filestem + str(mnt+1).zfill(2)+filetail
    print('Reading: ', filenm)
    data.append(read_one(filenm))

#data=xr.concat(data, dim='time')
# %%

all_data.to_netcdf('vel_may.nc')
# %%
