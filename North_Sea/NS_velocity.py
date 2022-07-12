#%%
from netCDF4 import Dataset,num2date 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
#import time
import xarray as xr
import utm
#import openpyxl
import pandas as pd
#import json
import re
from scipy import spatial
from calendar import monthrange
import sys, getopt

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
    tmpu=(~np.isnan(inxarr.u_eastward)).cumsum(dim='depth').argmax(dim='depth')
    tmpv=(~np.isnan(inxarr.v_northward)).cumsum(dim='depth').argmax(dim='depth')
    tmp=np.minimum(tmpu,tmpv)
    return inxarr.isel(depth=tmp)

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
    easting,northing, zone, letter=utm.from_latlon(inxarr.lat.values,inxarr.lon.values, force_zone_number=31)
    out=inxarr.copy()
    out=out.assign_coords(utm_E=(('Y','X'),easting))
    out=out.assign_coords(utm_N=(('Y','X'),northing))
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
def read_month(year=2022, month=5,pos=[60.7736192761523, 4.053348084930488],span=[10,10], save=False, verbose=True ):
    filestem='https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/NorKyst-800m_ZDEPTHS_his.an.'
    filetail='00.nc'
    
    data=[]
    for day in np.arange(monthrange(year,month)[1]):
        filenm=filestem + str(year) + str(month).zfill(2) + str(day+1).zfill(2)+filetail
        if verbose:
            print('Reading: ', filenm)
        data.append(read_one(filenm,pos, span))
    if verbose:
        print('Concating the data')
    data=xr.concat(data, dim='time')
    if save:
        outfile= 'NS_vel_'+str(year)+str(month).zfill(2) + '.nc'
        if verbose:
            print('Writing: '+outfile)
        data.to_netcdf(outfile)
    return data

# %%
def main(argv):
    year = 2022
    month = 5
    spanx=10
    spany=10
    lat=60.7736192761523
    lon= 4.05334808493048
    verbose=False
    try:
        opts, args = getopt.getopt(argv,"vhy:m:t:n:x:y:",["year=","month=","lat=","lon=", "spanx=","spany="])
    except getopt.GetoptError:
        print('python3 NS_velocity.py -y <year> -m <month> -t <lat> -n <lon> -x <span x> -y <span y>')
        print('or')
        print('python3 NS_velocity.py --year=<year> --month=<month> --lat=<lat> --lon=<lon> -x <span x> -y <span y>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print('python3 NS_velocity.py -y <year> -m <month> -t <lat> -n <lon> -x <span x> -y <span y>')
            print('or')
            print('python3 NS_velocity.py --year=<year> --month=<month> --lat=<lat> --lon=<lon> -x <span x> -y <span y>')
            sys.exit()
        elif opt == '-v':
            verbose = True
        elif opt in ("-y", "--year"):
            year = int(arg)
        elif opt in ("-m", "--month"):
            month = int(arg)
        elif opt in ("-t","--lat"):
            lat = float(arg)
        elif opt in ("-n", "--lon"):
            lon = float(arg)
        elif opt in ("-x", "--spanx"):
            spanx = int(arg)
        elif opt in ("-y", "--spany"):
            spany = int(arg)
        
    pos=[lat,lon]
    span=[spanx,spany]
    
    #print('read_month(year='+ str(year) + "month="+ str(month) + ",span=" + str(span) + ", pos= "+ pos+ ", save=True)" )
    read_month(year= year, month=month, span=span, pos= pos, save=True, verbose=verbose)    

if __name__ == '__main__':
    main(sys.argv[1:])
    #read_month(save=True)

# %%
