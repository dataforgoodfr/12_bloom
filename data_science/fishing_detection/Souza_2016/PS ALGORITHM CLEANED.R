#cleaned PS ALGORITHM

#### FIRST PART OF THIS CODE IS MADE TO BE RUN ON THE SERVER (may need to adjust directories)
# cd /data/boerder/gala_missing_vessels/
#   
# R

data<-read.csv('/data/boerder/gala_missing_vessels/356737000_algo.csv', head=TRUE)

library(doSNOW)
library(foreach)
library(snow)
library(sp)
library("rgdal")
library(rgeos)

colnames(data)

#rename
names(data)[names(data) == 'longitude'] <- 'LONGITUDE'
names(data)[names(data) == 'latitude'] <- 'LATITUDE'
names(data)[names(data) == 'mmsi'] <- 'MMSI'
names(data)[names(data) == 'datetime'] <- 'DATETIME'

#turn into numeric ### MIGHT NOT BE NECESSARY, CHECK!!!
#data$SOG=as.numeric(data$SOG)
#divide by 10 to get original speeds ### MIGHT NOT BE NECESSARY, CHECK!!!
#data$SOG = data$SOG/10 


#RUN THIS CODE ON THE SERVER (additional data required (ne_10m_coastline and monthly files need to be linked to respective directories!!!)
distshore<-function(x,metric,clustersize=3){
  
  cl <- makeCluster(clustersize, type='SOCK')
  
  registerDoSNOW(cl)
  
  wgs.84<-"+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  mollweide<-'+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
  dtsp<-SpatialPoints(x[, c('LONGITUDE','LATITUDE')], proj4string = CRS(wgs.84))
  coast<-readOGR(dsn = "/data/boerder/scripts/ne_10m_coastline/", layer = 'ne_10m_coastline', p4s=wgs.84)
  coast.moll<-spTransform(coast, CRS(mollweide))
  dtsp.moll<-spTransform(dtsp, CRS(mollweide))
  getdistparallel <- function(n){
    
    foreach(i=1:n, .combine = 'c', .packages = 'rgeos', .inorder = TRUE,
            .export=c('dtsp.moll','coast.moll')) %dopar% gDistance(dtsp.moll[i], coast.moll)
    
  }
  res<-getdistparallel(nrow(x))
  stopCluster(cl)
  if (metric=='m'){
    return(res)
  }
  if (metric=='km'){
    return(res/1000)
  }
  if (metric=='miles'){
    return(res/1000)*0.62
  }
}


data[,'date']<-as.POSIXct(data$DATETIME, format="%Y-%m-%d %H:%M:%OS")
data<-data[order(data$MMSI,data$date),]  

data<-data[!is.na(data$date),] #Removes incorrect date values from database
data[,'distshore']<-distshore(data,'km',40)

data[,'local_date']<-as.POSIXct(data$date, format="%Y-%m-%d %H:%M:%OS")+((data$LONGITUDE*24)/360)*3600
data[,'searchdataday']<-paste('2012',substr(data$date, 5, 14),'00:00', sep='')
data<-data[!abs(data$LONGITUDE)>180,]


### BEFORE THIS STEP MAKE SURE THE MONTHLY FILES ARE IN THE SAME FOLDER AS THE DATA
month<-c('01','02','03','04','05','06','07','08','09','10','11','12')#
lstfiles<-c('daynightresult-Jan.RData',
            'daynightresult-Feb-Mar.RData',
            '',
            'daynightresult-Apr-May.RData',
            '',
            'daynightresult-Jun-Jul.RData',
            '',
            'daynightresult-Aug-Sep.RData',
            '',
            'daynightresult-Oct-Nov.RData',
            '',
            'daynightresult-Dec.RData')
count<-1
for (m in month){
  if (lstfiles[count]!='')
    load(lstfiles[count])
  mondata<-data[substr(data$date, 6, 7)==m,]
  if (nrow(mondata)>0){
    for (i in 1:nrow(mondata)){
      tmp<-dfres[as.character(dfres$date)==mondata[i,'searchdataday'],'d'][[1]]
      mondata[i,'day']<-tmp[tmp$lon==ceiling(mondata[i,'LONGITUDE'])&tmp$lat==floor(mondata[i,'LATITUDE']),'Bo0']
    }
    
    data[substr(data$date, 6, 7)==m,'day']<-mondata$day
  }
  count<-count+1
}
data[,'distshore']<-distshore(data,'km',40)
data[,'SOG']<-as.numeric(data[,'SOG'])
data[is.na(data$SOG),'SOG'] = 0
data[data$SOG=='None','SOG'] = 0

data[(data$SOG)<=2.5&data$distshore>=10&data$day>0,'SPEEDTHRES']<-1
data[(data$SOG)<=2.5&data$distshore>=10&data$day==0,'SPEEDTHRES']<-0
data[(data$SOG)>=2.5&data$distshore>=10,'SPEEDTHRES']<-0
data[is.na(data$SPEEDTHRES),'SPEEDTHRES']<-0


###############FROM HERE ON WORK WITH ALGORITHM OUTPUTS (can be done on local computer)

#find outliers with moving window
avgsog <- function (t, size, degree) {
  
  bollinger<-matrix (nrow=length(t)-(size-1),
                     ncol=2)
  for (i in 1:(length(t)-(size-1))){   
    bollinger[i,1]<-mean(t[i:(i+(size-1))])
    #    bollinger[i,2]<-sd(t[i:(i+(size-1))])
    bollinger[i,2]<-bollinger[i,1]+(sd(t[i:(i+(size-1))])*degree) 
  }  
  return(bollinger)
}
windowsize<-5
datasog<-avgsog(data$SOG, windowsize, 1)

data[1:windowsize,'sdsog']<-datasog[1,2]
data[1:windowsize,'meansog']<-datasog[1,1]

data[windowsize:nrow(data),c('meansog','sdsog')]<-datasog[,1:2]

data[data$SOG>(data$sdsog)&data$SPEEDTHRES==0&data$day>0&data$distshore>10, 'SPEEDTHRES']<-2


#delete outliers before calculating bursts
data<-data[!data$SPEEDTHRES==2, ]

#this is the new code including detection of outliers
findburstK<-function(x, deltatime){
  
  burst<-rep(0,nrow(x))
  count<-1
  if (x[1,'SPEEDTHRES']==1) burst[1]<-1
  for (i in 2:nrow(x)){
    if (x[i-1,'SPEEDTHRES']==x[i,'SPEEDTHRES'] && x[i,'SPEEDTHRES']==1 ){
     
      burst[i-1]<-count
      burst[i]<-count
    } else if (x[i-1,'SPEEDTHRES']!=x[i,'SPEEDTHRES'] && x[i-1,'SPEEDTHRES']==1 && x[i,'SPEEDTHRES']==2){
      burst[i-1]<-count
      burst[i]<-count
    }else if (x[i-1,'SPEEDTHRES']!=x[i,'SPEEDTHRES'] && x[i-1,'SPEEDTHRES']==2 && x[i,'SPEEDTHRES']==1){
      burst[i-1]<-count
      burst[i]<-count
    }else
      count<-count+1
    
  }
  burst
  
}


data[!is.na(data$SPEEDTHRES),'burstS']<-findburstK(data[!is.na(data$SPEEDTHRES),],10800)

sumburstsK<-function(x){
  bursts<-unique(x[!is.na(x$SPEEDTHRES),'burstS'])
  bursts<-bursts[bursts!=0]
  dfres<-data.frame(burstid=integer(length(bursts)),
                    totaltime=numeric(length(bursts)),
                    nrpoints=integer(length(bursts)))
  count<-1
  for (i in bursts){
    tmp<-x[!is.na(x$burstS)&x$burstS==i,]
    dfres$totaltime[count]<- difftime(tmp[nrow(tmp),'date'], tmp[1,'date'], tz='UTC',
                                      units = "hours") 
    dfres$burstid[count]<-i
    dfres$nrpoints[count]<-nrow(tmp)
    count<-count+1
    
  }
  dfres
}

addtimeK<-function(x,burstsum){
  
  
  for (i in burstsum$burstid){
    
    x[x$burstS==i&!is.na(x$burstS),'totaltimeK']<-rep(burstsum[burstsum$burstid==i,'totaltime'],burstsum[burstsum$burstid==i,'nrpoints'])
  }
  
  x
}

ksum<-sumburstsK(data[!is.na(data$SPEEDTHRES),])

data<-addtimeK(data,ksum)

#number of individual bursts (0 is counted, subtract -1!!!)
unique(data$burstS)

#delete all bursts = 0
data<-data[!data$burstS==0, ]


#save
write.csv(data, "4missing vessels_algo complete.csv", row.names=FALSE)


#delete all bursts with totaltimeK <0.2
data_red <-data[!data$totaltimeK<0.2, ]

#select first row for each unique burstS
rows <- data_red[!duplicated(data_red$burstS),]

#save
write.csv(rows, "356737000_algo_firstburst.csv", row.names=FALSE)



