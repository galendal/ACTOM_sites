#%%
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
from windrose import WindroseAxes
from matplotlib.dates import date2num
from utide import solve, reconstruct
import numpy as np
import pandas as pd
from windrose import WindroseAxes
import hvplot.xarray
from eofs.xarray import Eof
import glob

from eofs.multivariate.standard import MultivariateEof

# %%
data_path='./new_5km-radius/'
files=sorted(glob.glob('new_5km-radius/GOM-1-*2012*'))
vel_arr=[]
for file in files:
    tmp=xr.open_dataset(file).load()
    tmp.close()
    vel_arr.append(tmp)

data=xr.merge(vel_arr)
# %%
data['speed']=np.sqrt(data.u**2+data.v**2)
angles=np.arctan2(data['u'],data['v'])
data['direction']=(angles + 2 * np.pi) % (2 * np.pi)*(180/np.pi)
data['ocean_depth']= data.z.min(dim='depth')
# %%
data=data.set_coords('z')
data=data.set_coords('lat')
data=data.set_coords('lon')
# %%
data_stacked=data.stack(zz=['node','depth'])

#%%
msolver = MultivariateEof([data_stacked.u.data, data_stacked.v.data])

#%%
eofs_u, eofs_v= msolver.eofs()
eofs_pcs=msolver.pcs()
eofs_eigen=msolver.eigenvalues()

# %%
data_stacked['eofs_u']=(['mode','zz'],eofs_u)
data_stacked['eofs_v']=(['mode','zz'],eofs_v)
data_stacked['eofs_eig']=(['mode'],eofs_eigen)
data_stacked['eofs_pcs']=(['ocean_time','mode'],eofs_pcs)
# %%
data_stacked.unstack('zz').to_netcdf(data_path+'eof.nc')
# %%
data=data_stacked.unstack('zz')
# %%
data
# %%
tmp=data.isel(depth=-1,mode=0).eofs_u


# %%

fig,  ax2 = plt.subplots(nrows=1)
ax2.tricontour(tmp.lon, tmp.lat, tmp, levels=14, colors='k')
ax2.tricontourf(tmp.lon, tmp.lat, tmp)
ax2.scatter(tmp.lon,tmp.lat, color='k')
# %%
tmp
# %%
plt.matshow(np.corrcoef(data.isel(depth=0,mode=0).eofs_u.data.T,data.isel(depth=0,mode=0).eofs_v.data.T))
plt.colorbar()
#%%
data.isel(depth=0).u
# %%
data.isel(depth=0,mode=0).eofs_u
# %% http://brunnur.vedur.is/pub/halldor/PICKUP/eof.pdf
uu=(data_stacked.u-data_stacked.u.mean(dim='ocean_time')).data
vv=(data_stacked.v-data_stacked.v.mean(dim='ocean_time')).data
# %%
C=np.dot(uu.T, vv)
# %%
U,L,Vh = np.linalg.svd(C)

# %%
V=Vh.T
#%%
SCF=L/np.sum(L)
plt.plot(SCF)
plt.xlim(0,10)
plt.plot(np.cumsum(SCF))
# %%
A=uu@U
B=vv@V
# %%
re_U=A@U.T
re_V=B@V.T
# %%
