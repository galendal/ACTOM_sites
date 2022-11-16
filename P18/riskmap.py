#%%
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
#import time
import xarray as xr
import sys, getopt
import os
import glob
# %%
def plot_risk_map(file='Q13_Q16_k1k2filt_10_10_destriping_0_01_amplitude_AGF_2_netcdf.nc',
path='P18 data/'):
    filenm=path+file
    data=xr.open_dataset(filenm)
    data=data.set_coords(('coordX','coordY'))
    data['normed relative probability']=data.location_probability/data.location_probability.max()
    data['log of normed relative probability']=np.log(data['normed relative probability'])
    data.close()

    data['log of normed relative probability'].plot.contourf(x='coordX',y='coordY', vmin=-2, cmap='Oranges')

    plt.xlabel('x-direction (m)')
    plt.ylabel('y-direction (m)')
#plt.xlim(560000,)
#plt.ylim(5770000)
    plt.gca().set_aspect('equal')
    plt.savefig(os.path.splitext(filenm)[0]+'.png')
    print(os.path.splitext(filenm)[0]+'.png')
    plt.close()
# %%
plot_risk_map(file='Q13_GSZ11_CGGV12_Final_PrSTM_stack_amplitude_AGF_2_netcdf.nc')
# %%
files=glob.glob('../Riskmaps/*.nc')
for file in files:
    plot_risk_map(file=file, path='')

# %%
