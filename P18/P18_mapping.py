#%%
from cProfile import label
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
from itertools import islice
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

#%%
def dms2dd(degrees, minutes, seconds, direction='E'):
    dd = degrees + minutes/60 + seconds/(60*60)
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd

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
# %%


# %%
def get_risk_map(file='Q13_GSZ11_CGGV12_Final_PrSTM_stack_amplitude_AGF_2_netcdf_lonlat.nc',
path='../Riskmaps/'):
    filenm=path+file
    data=xr.open_dataset(filenm)

    data=data.set_coords(('coordLON','coordLAT'))
    
    data.close()

    return data



#%%
    
# %% Read coordinates from Sarah


# set up orthographic map projection with
# perspective of satellite looking down at 50N, 100W.
# use low resolution coastlines.

def make_map_P18(inmap, margin=[0.5, 0.5], savefig=True):
    
    p=inmap.location_probability;

    pp=p.values.flatten()
    p=p/sum(pp)

    logp=np.log(p)
    
    lllon = inmap.coordLON.min()-margin[0]
    urlon = inmap.coordLON.max()+margin[0]
    urlat = inmap.coordLAT.max()+margin[1]   
    lllat = inmap.coordLAT.min()-margin[1]


    fig = plt.figure()
    ax = fig.add_subplot(111)

    map = Basemap(
        projection='cyl',
        lat_0=(urlat-lllat)/2,
        lon_0=(urlon-lllon)/2,
        resolution='h',
        llcrnrlat=lllat, 
        urcrnrlat=urlat, 
        llcrnrlon=lllon, 
        urcrnrlon=urlon
        )
# draw coastlines, country boundaries, fill continents.
    map.etopo(scale=0.9,alpha=0.5)
    map.drawcoastlines(linewidth=0.2, color='#cd5b45')
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='coral',lake_color='aqua')
#Houston 29.749907, -95.358421
    x, y = map(4.462456,51.926517) # Houston
    plt.scatter(x, y, 20, marker='o', color='Black')
    plt.annotate('Rotterdam', xy=(x, y))

#The latitude of New Orleans, LA, USA is 29.951065, and the longitude is -90.071533.
    x, y = map(4.288788,52.078663) # Houston
    plt.scatter(x, y, 20, marker='o', color='Black')
    plt.annotate('Haag', xy=(x, y))   


    
    lons=inmap['coordLON']
    lats=inmap['coordLAT']
    x, y = map(lons, lats)  # transform coordinates
    map.pcolormesh(x, y, logp,shading='auto', label='log(p)')
    cbar=map.colorbar()
    cbar.set_label('log of relative probability')
 #   plt.scatter(x, y, 10, marker='o', color='Blue')     

    x=3.939394
    y=52.16216
    plt.scatter(x, y, 20, marker='x', color='Red') 

    
# Zoomed plot
    llcrnrlon=lons.min().data
    llcrnrlat=lats.min().data
    urcrnrlon=lons.max().data
    urcrnrlat=lats.max().data

    axins = zoomed_inset_axes(ax, 2, loc=1)
    axins.set_xlim(lons.min(), lons.max())
    axins.set_ylim(lats.min(), lats.max())

    map2 = Basemap(
        llcrnrlon=llcrnrlon,
        llcrnrlat=llcrnrlat,
        urcrnrlon=urcrnrlon,
        urcrnrlat=urcrnrlat, 
        ax=axins,
#    suppress_ticks=False
        )
    map2.drawmapboundary(fill_color='#BCD2E8')
    map2.etopo(scale=0.9,alpha=0.5)
 #   map2.drawmeridians([3.8,4,4.2], labels=[0,0,0,1])
 #   map2.drawparallels([60.5,60.7,60.9], labels=[0,1,0,0])
    map2.fillcontinents(color='#ddaa66', lake_color='#7777ff', zorder=0)
#map2.drawcoastlines()
#map2.drawcountries()

    
    x, y = map2(lons, lats)  # transform coordinates
    map2.pcolormesh(x, y, logp,shading='auto', label='log(p)')
    
    mark_inset(ax, axins, loc1=2, loc2=4)#, fc="none", ec="0.5")
    

    plt.show()
    if savefig:
        fig.savefig('P18_map.png')

    return 
#%%
map=get_risk_map()
# %%
make_map_P18(map, margin=[0.5, 0.5], savefig=False)
# %%
