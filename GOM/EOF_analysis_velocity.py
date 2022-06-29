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
import pyts as pyts
import pyts.image as pytsimag

from eofs.multivariate.standard import MultivariateEof

# %%
# def my_tide(data, t_name='ocean_time',space_name='zz',u_name='u',v_name='v', tide_name='_tide'):
#     t=data[t_name].data
#     out=data[[u_name,v_name]].copy()
#     out[u_name+tide_name]=xr.zeros_like(out[u_name])
#     out[v_name+tide_name]=xr.zeros_like(out[v_name])
#     for node in out[space_name].values:
#         lat=data.isel(node=node).lat.values
#         tmp_xr=[]
#         for depth in data.depth.values:
#             uvel=data.isel(node=node,depth=depth).u.values
#             vvel=data.isel(node=node,depth=depth).v.values
#             coef=solve(t,u=uvel,v=vvel,lat=lat)
#             tide=reconstruct(t, coef)
#             velocities.u_tide[:,node,depth]=tide.u
#             velocities.v_tide[:,node,depth]=tide.v

#     return out

def my_svd(data, tname='ocean_time', uname='u', vname='v',tresh=0.90,plot=False):
    u_mean=data[uname].mean(dim=tname)
    v_mean=data[uname].mean(dim=tname)
    uu=(data[uname]-u_mean).data
    vv=(data[vname]-v_mean).data

    C=np.dot(uu.T, vv)
    U,L,Vh = np.linalg.svd(C)
    
    V=Vh.T
    SCF=L/np.sum(L)
    indx=int(np.argwhere(np.cumsum(SCF)>tresh)[0])+1
    

    U=U[:,0:indx]
    V=V[:,0:indx]
    L=L[0:indx]
    SCF=SCF[0:indx]
    A=uu@U
    B=vv@V
    
    re_U=A@U.T
    re_V=B@V.T
    if plot:
        plt.plot(SCF)
        plt.xlim(0,10)
        plt.plot(np.cumsum(SCF))
    print(A.shape)
    out=data.copy()
    out['u_pcs']=((tname,'mode'),A)
    out['v_pcs']=((tname,'mode'),B)
    out['u_eofs']=((u_mean.dims + ('mode',)),U)
    out['v_eofs']=((v_mean.dims + ('mode',)),V)
    out['eigen']=(('mode'),L)
    out['SCF']=(('mode'),SCF)

    return out


#%%
def plot_eofs(data):
    fig,  ax2 = plt.subplots(nrows=1)
    ax2.tricontour(data.lon, data.lat, data, levels=14, colors='k')
    ax2.tricontourf(data.lon, data.lat, data)
    ax2.scatter(data.lon,data.lat, color='k')
    ax2.colorbar()


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
U,L,V = my_svd(uu, vv)
# %%
A=uu@U
B=vv@V
# %%
re_U=A@U.T
re_V=B@V.T
# %%
data
# %%
t=data['ocean_time'].data
velocities=data[['u','v']].copy()
velocities['u_tide']=xr.zeros_like(velocities.u)
velocities['v_tide']=xr.zeros_like(velocities.v)
#%%
for node in data.node.values:
    lat=data.isel(node=node,depth=0).lat.values
    tmp_xr=[]
    for depth in data.depth.values:
        uvel=data.isel(node=node,depth=depth).u.values
        vvel=data.isel(node=node,depth=depth).v.values
        coef=solve(t,u=uvel,v=vvel,lat=lat)
        tide=reconstruct(t, coef)
        velocities.u_tide[:,node,depth]=tide.u
        velocities.v_tide[:,node,depth]=tide.v

#%%
velocities['u_residue']=velocities.u-velocities.u_tide
velocities['v_residue']=velocities.v-velocities.v_tide   
# %%
velocities.to_netcdf('velocities.nc')
# %%
uu=(velocities.u_residue-velocities.u_residue.mean(dim='ocean_time'))
vv=(velocities.v_residue-velocities.v_residue.mean(dim='ocean_time'))

# %%
U,L,V = my_svd(uu.isel(depth=0), vv.isel(depth=0), plot=True)
# %%
L
# %%
np.cumsum(L)/sum(L)
# %%
A=uu.isel(depth=0).data@U
B=vv.isel(depth=0).data@V
# %%

# %%
uu=data.isel(depth=0).u-data.isel(depth=0).u.mean(dim='ocean_time')
vv=data.isel(depth=0).v-data.isel(depth=0).v.mean(dim='ocean_time')
# %%
tmp=uu.data@uu.T.data
# %%
