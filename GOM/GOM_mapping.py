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
def read_velocity_area(file='new_5km-radius/GOM-1-2012-07.nc'):
    vel=xr.open_dataset(file).load()
    vel.close()
    vel
    return vel



#%%
    
# %% Read coordinates from Sarah


# set up orthographic map projection with
# perspective of satellite looking down at 50N, 100W.
# use low resolution coastlines.

def make_map_GOM(vel, margin=[0.5, 0.5], savefig=True):

    lllon = vel.lon.min()-margin[0]
    urlon = vel.lon.max()+margin[0]
    urlat = vel.lat.max()+margin[1]   
    lllat = vel.lat.min()-margin[1]
    fig = plt.figure()
    ax = fig.add_subplot(111)

    map = Basemap(
        projection='cyl',
        lat_0=60,lon_0=4,
        resolution='h',
        llcrnrlat=lllat, 
        urcrnrlat=urlat, 
        llcrnrlon=lllon, 
        urcrnrlon=urlon
        )
# draw coastlines, country boundaries, fill continents.
    map.etopo(scale=0.9,alpha=0.5)
    map.drawcoastlines(linewidth=0.25, color='#cd5b45')
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='coral',lake_color='aqua')


    return

#%%
#xmin, ymin = map(lllon, lllat)
#xmax, ymax = map(urlon, urlat)
    lons=wells['EW decimal degrees']
    lats=wells['NS decimal degrees']
    x, y = map(lons, lats)  # transform coordinates
    plt.scatter(x, y, 10, marker='o', color='Blue') 

    lons=other['lon']
    lats=other['lat']
    x, y = map(lons, lats)  # transform coordinates
    plt.scatter(x, y, 10, marker='o', color='Green') 

    x, y = map(5.32415, 60.39299) # Bergen
    plt.scatter(x, y, 20, marker='o', color='Black')
    plt.annotate('Bergen', xy=(x, y))

# Haugesund 59.41378, 5.268
    x, y = map(5.268, 59.41378) # Haugesund
    plt.scatter(x, y, 20, marker='o', color='Black')
    plt.annotate('Haugesund', xy=(x, y))#, weight='bold')

#Ålesund 62.47225, 6.15492
#x, y = map(6.15492, 62.47225) # Ålesund
#plt.scatter(x, y, 20, marker='o', color='Black')
#plt.annotate('Ålesund', xy=(x, y))

#Mongstad 60.81129 5.032976
    x, y = map(5.032976, 60.81129) # Mongstad
    plt.scatter(x, y, 20, marker='o', color='Black')
    plt.annotate('Mongstad', xy=(x, y))

#Stavanger 58.969975, 5.733107
    x, y = map(5.733107, 58.969975) # Bergen
    plt.scatter(x, y, 20, marker='o')
    plt.annotate('Stavanger', xy=(x, y), color='Black')
# Zoomed plot
    axins = zoomed_inset_axes(ax, 6.1, loc=1)
    axins.set_xlim(4, 5)
    axins.set_ylim(61, 62)

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
    map2.drawmeridians([3.8,4,4.2], labels=[0,0,0,1])
    map2.drawparallels([60.5,60.7,60.9], labels=[0,1,0,0])
#map2.fillcontinents(color='#ddaa66', lake_color='#7777ff', zorder=0)
#map2.drawcoastlines()
#map2.drawcountries()

    x, y = map2(lons, lats)  # transform coordinates
    map2.scatter(x, y, 10, marker='o', color='Green') 
    lons=data['EW decimal degrees']
    lats=data['NS decimal degrees']
    x, y = map2(lons, lats)  # transform coordinates
    map2.scatter(x, y, 10, marker='o', color='Blue')

    mark_inset(ax, axins, loc1=2, loc2=4)#, fc="none", ec="0.5")
    plt.show()
    if savefig:
        fig.savefig('NS_map.png')
#%%
pos=read_sarah()
wells=read_NPD_xlsx()
# %%
make_map_NS(wells=wells,other=pos)
# %%
