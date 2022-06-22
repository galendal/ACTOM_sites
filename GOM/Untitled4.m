url = 'https://pong.tamu.edu/thredds/dodsC/NcML/txla_hindcast_agg';
ncid = netcdf.open(url);

point1=[-94.134, 29.571];
point2=[-93.981, 29.568];

outfile1='point1.nc';
outfile2='point2.nc';

timevar ='ocean_time';
time =  ncread(url,'ocean_time');
year= str2num(datestr(time./86400 + datenum(1970,1,1),'yyyy'));
month= str2num(datestr(time./86400 + datenum(1970,1,1),'mm'));
clear time
timeend=18936;
Yearrun=year(timeend+1);
Monthrun=month(timeend+1)-1;

%for loop each month
while Yearrun < max(year)
    formatSpec = 'restart from: %i \n';
    timestart=timeend+1;
    fprintf(formatSpec,timestart)
    %    Yearrun=Yearrun+1;
    Monthrun=Monthrun+1;
    if Monthrun == 13
        Monthrun=1;
        Yearrun=Yearrun+1;
    end
    if Monthrun == 12
        timeend=find(1 == month(timestart:numel(month)),1)-1+timestart;
    else
        timeend=find(Monthrun+1 == month(timestart:numel(month)),1)-1+timestart;
    end
    
    if Monthrun >= 10
        outfile1= convertStringsToChars(join(['GOM-1-',string(Yearrun),'-',string(Monthrun),'.nc'],''));
        outfile2= convertStringsToChars(join(['GOM-2-',string(Yearrun),'-',string(Monthrun),'.nc'],''));
    else
        outfile1= convertStringsToChars(join(['GOM-1-',string(Yearrun),'-0',string(Monthrun),'.nc'],''));
        outfile2= convertStringsToChars(join(['GOM-2-',string(Yearrun),'-0',string(Monthrun),'.nc'],''));
    end
    
    time =  ncread(url,'ocean_time',timestart,timeend-timestart+1);
    
    nccreate(outfile1,'ocean_time',...
        'Dimensions',{'ocean_time',numel(time)},...
        'Format','netcdf4')
    ncwrite(outfile1,'ocean_time',time)
    nccreate(outfile2,'ocean_time',...
        'Dimensions',{'ocean_time',numel(time)},...
        'Format','netcdf4')
    ncwrite(outfile2,'ocean_time',time)
    
    vinfo = ncinfo(url,'ocean_time');
    varid = netcdf.inqVarID(ncid,'ocean_time');
    
    for B=1:numel(vinfo.Attributes)
        E=netcdf.inqAttName(ncid,varid,B-1);
        if numel(E)==10
            if E~='_FillValue'
                attvalue = ncreadatt(url,'ocean_time',E);
                ncwriteatt(outfile1,'ocean_time',E,attvalue);
                ncwriteatt(outfile2,'ocean_time',E,attvalue);
            end
        else
            attvalue = ncreadatt(url,'ocean_time',E);
            ncwriteatt(outfile1,'ocean_time',E,attvalue);
            ncwriteatt(outfile2,'ocean_time',E,attvalue);
        end
    end
    
    sr=ncread(url,'s_rho');
    h=ncread(url,'h');
    depth = repmat(h,1,1,numel(sr));
    for B=1:numel(sr)
        depth(:,:,B)=depth(:,:,B).*sr(B);
    end
    
    nccreate(outfile1,'depth',...
        'Dimensions',{'depth',numel(sr)},...
        'Format','netcdf4');
    
    nccreate(outfile2,'depth',...
        'Dimensions',{'depth',numel(sr)},...
        'Format','netcdf4');
    
    ncwriteatt(outfile1,'depth','units','meters depth');
    ncwriteatt(outfile2,'depth','units','meters depth');
    
    %
    %     vinfo = ncinfo(url,'s_rho');
    %     varid = netcdf.inqVarID(ncid,'s_rho');
    %
    %     for B=1:numel(vinfo.Attributes)
    %         E=netcdf.inqAttName(ncid,varid,B-1);
    %         if numel(E)==10
    %             if E~='_FillValue'
    %                 attvalue = ncreadatt(url,'s_rho',E);
    %                 ncwriteatt(outfile1,'s_rho',E,attvalue);
    %                 ncwriteatt(outfile2,'s_rho',E,attvalue);
    %             end
    %         else
    %             attvalue = ncreadatt(url,'s_rho',E);
    %             ncwriteatt(outfile1,'s_rho',E,attvalue);
    %             ncwriteatt(outfile2,'s_rho',E,attvalue);
    %         end
    %     end
    %
    %     vinfo = ncinfo(url,'s_w');
    %     varid = netcdf.inqVarID(ncid,'s_w');
    %
    %     for B=1:numel(vinfo.Attributes)
    %         E=netcdf.inqAttName(ncid,varid,B-1);
    %         if numel(E)==10
    %             if E~='_FillValue'
    %                 attvalue = ncreadatt(url,'s_w',E);
    %                 ncwriteatt(outfile1,'s_w',E,attvalue);
    %                 ncwriteatt(outfile2,'s_w',E,attvalue);
    %             end
    %         else
    %             attvalue = ncreadatt(url,'s_w',E);
    %             ncwriteatt(outfile1,'s_w',E,attvalue);
    %             ncwriteatt(outfile2,'s_w',E,attvalue);
    %         end
    %     end
    
    
    for C= 1:3
        if C==1
            lonv='lon_rho';
            latv='lat_rho';
        elseif C==2
            lonv='lon_u';
            latv='lat_u';
        elseif C==3
            lonv='lon_v';
            latv='lat_v';
        end
        
        lon=ncread(url,lonv);
        lat=ncread(url,latv);
        
        if C==1
            nccreate(outfile1,'lon',...
                'Dimensions',{'lon',1},...
                'Format','netcdf4')
            nccreate(outfile1,'lat',...
                'Dimensions',{'lat',1},...
                'Format','netcdf4')
            nccreate(outfile2,'lon',...
                'Dimensions',{'lon',1},...
                'Format','netcdf4')
            nccreate(outfile2,'lat',...
                'Dimensions',{'lat',1},...
                'Format','netcdf4')
        end
        
        dist1=sqrt((abs(point1(2)-lat(1,1))^2)+(abs(point1(1)-lon(1,1))^2));
        dist2=sqrt((abs(point2(2)-lat(1,1))^2)+(abs(point2(1)-lon(1,1))^2));
        for A=1:numel(lat(:,1))
            for B=1:numel(lat(1,:))
                dist1new=sqrt((abs(point1(2)-lat(A,B))^2)+(abs(point1(1)-lon(A,B))^2));
                dist2new=sqrt((abs(point2(2)-lat(A,B))^2)+(abs(point2(1)-lon(A,B))^2));
                if dist1new<=dist1
                    dist1=dist1new;
                    pos1=[A,B];
                end
                if dist2new<=dist2
                    dist2=dist2new;
                    pos2=[A,B];
                end
            end
        end
        
        if C==1
            ncwrite(outfile1,'lon',lon(pos1(1),pos1(2)))
            ncwrite(outfile1,'lat',lat(pos1(1),pos1(2)))
            ncwrite(outfile2,'lon',lon(pos2(1),pos2(2)))
            ncwrite(outfile2,'lat',lat(pos2(1),pos2(2)))
            
            vinfo = ncinfo(url,lonv);
            varid = netcdf.inqVarID(ncid,lonv);
            
            for B=1:numel(vinfo.Attributes)
                E=netcdf.inqAttName(ncid,varid,B-1);
                if numel(E)==10
                    if E~='_FillValue'
                        attvalue = ncreadatt(url,lonv,E);
                        ncwriteatt(outfile1,'lon',E,attvalue);
                        ncwriteatt(outfile2,'lon',E,attvalue);
                    end
                else
                    attvalue = ncreadatt(url,lonv,E);
                    ncwriteatt(outfile1,'lon',E,attvalue);
                    ncwriteatt(outfile2,'lon',E,attvalue);
                end
            end
            
            vinfo = ncinfo(url,latv);
            varid = netcdf.inqVarID(ncid,latv);
            
            for B=1:numel(vinfo.Attributes)
                E=netcdf.inqAttName(ncid,varid,B-1);
                if numel(E)==10
                    if E~='_FillValue'
                        attvalue = ncreadatt(url,latv,E);
                        ncwriteatt(outfile1,'lat',E,attvalue);
                        ncwriteatt(outfile2,'lat',E,attvalue);
                    end
                else
                    attvalue = ncreadatt(url,latv,E);
                    ncwriteatt(outfile1,'lat',E,attvalue);
                    ncwriteatt(outfile2,'lat',E,attvalue);
                end
            end

        depthout(:)=depth(pos1(1),pos1(2),:);
        ncwrite(outfile1,'depth',depthout)
        ncwrite(outfile2,'depth',depthout)            
            
        end

        
        clearvars -except C D url point1 point2 pos1 pos2 outfile1 outfile2 timestart timeend lonv latv ncid year Yearrun Monthrun month
        
        if C==1
            variable=["temp" "salt" "w"]; 
        elseif C==2
            variable="u";
        elseif C==3
            variable="v";
        end
        
        for A=1:numel(variable)
            
            vinfo = ncinfo(url,char(variable(A)));
            varid = netcdf.inqVarID(ncid,char(variable(A)));
            var = ncread(url,char(variable(A)),[pos1(1) pos1(2) 1 timestart],[1 1 30 (timeend-timestart+1)]);
            
            nccreate(outfile1,char(variable(A)),...
                'Dimensions',{'lon',numel(var(:,1,1,1)),...
                'lat',numel(var(1,:,1,1)),...
                'depth',numel(var(1,1,:,1)),...
                vinfo.Dimensions(4).Name,numel(var(1,1,1,:))},...
                'Format','netcdf4')
            
            ncwrite(outfile1,char(variable(A)),var)
            
            clear var
            
            var = ncread(url,char(variable(A)),[pos2(1) pos2(2) 1 timestart],[1 1 30 (timeend-timestart+1)]);
            
            nccreate(outfile2,char(variable(A)),...
                'Dimensions',{'lon',numel(var(:,1,1,1)),...
                'lat',numel(var(1,:,1,1)),...
                'depth',numel(var(1,1,:,1)),...
                vinfo.Dimensions(4).Name,numel(var(1,1,1,:))},...
                'Format','netcdf4')
            
            ncwrite(outfile2,char(variable(A)),var)
            
            clear var
            
            for B=1:numel(vinfo.Attributes)
                E=netcdf.inqAttName(ncid,varid,B-1);
                if numel(E)==10
                    if E~='_FillValue'
                        attvalue = ncreadatt(url,char(variable(A)),E);
                        ncwriteatt(outfile1,char(variable(A)),E,attvalue);
                        ncwriteatt(outfile2,char(variable(A)),E,attvalue);
                    end
                else
                    attvalue = ncreadatt(url,char(variable(A)),E);
                    ncwriteatt(outfile1,char(variable(A)),E,attvalue);
                    ncwriteatt(outfile2,char(variable(A)),E,attvalue);
                end
            end
        end
    end
    [ndims nvars natts dimm] = netcdf.inq(ncid);
    
    for A=1:natts
        C=netcdf.inqAttName(ncid,netcdf.getConstant('NC_GLOBAL'),A-1);
        attvalue = ncreadatt(url,'/',C);
        ncwriteatt(outfile1,'/',C,attvalue);
        ncwriteatt(outfile2,'/',C,attvalue);
    end
    
    clearvars -except C D url point1 point2 pos1 pos2 outfile1 outfile2 timestart timeend ncid year Yearrun Monthrun month
    
end