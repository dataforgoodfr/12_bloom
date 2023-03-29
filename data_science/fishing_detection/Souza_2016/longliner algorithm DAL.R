#!/usr/bin/env Rscript


library(doSNOW)
library(foreach)
library(snow)
library(sp)
library("rgdal")
library(rgeos)
library(adehabitatLT)
library(adehabitatHR)
library(adehabitatHS)
library(fpc)
#library(caret)

tz = "UTC"

# Parse commandline arguments
args = commandArgs(trailingOnly=TRUE)
if (length(args) != 3){
    print("Usage: INFILE OUTFILE COAST_DIR")
    quit(1)
}
infile = args[1]
outfile = args[2]
coast_dir = args[3]



difftimes<-function(x){x <-rev( x ); rev(difftime(x[1:(length(x)-1)] , x[2:length(x)] ))}


#The function longlinerpreds assumes that the csv header contains the following fields:
#<MMSI, LONGITUDE, LATITUDE, date>. R is a case sensitive language, so the names must be
#exactly as described. The date field assumes the following format:"%Y-%m-%d %H:%M:%OS".
#Function distshore will require you to download the Natural Earth data available in this site
# http://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/


#http://stackoverflow.com/questions/27697504/ocean-latitude-longitude-point-distance-from-shore
distshore<-function(x,metric,clustersize=3,dsn=coast_dir){
  wgs.84<-"+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  mollweide<-'+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
  dtsp<-SpatialPoints(x[, c('LONGITUDE','LATITUDE')], proj4string = CRS(wgs.84))
  coast<-readOGR(dsn = dsn, layer = '10m_coastline', p4s=wgs.84)
  coast.moll<-spTransform(coast, CRS(mollweide))
  dtsp.moll<-spTransform(dtsp, CRS(mollweide))
  cl <- makeCluster(clustersize, type='SOCK')

  registerDoSNOW(cl)

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



data<-read.csv(infile, head=TRUE)
data[,'date']<-as.POSIXct(data$TIME, format="%Y%m%d_%H%M%OS", tz=tz)

data[,'distshore'] <- distshore(data,'km')




longlinerpreds<-function(dframe, segs=70, kmax=200){

  data<-dframe
  data<-data[order(data$MMSI,data$date),]
  data<-data[!is.na(data$date),]
  data[,'difftime']<-c(0,difftimes(data$date))
  newdata <- as.ltraj(data[data$difftime>0, c('LATITUDE', 'LONGITUDE')], date=as.POSIXct(data[data$difftime>0, 'date'], format="%Y-%m-%d %H:%M:%OS", tz=tz), id=data[data$difftime>0, 'MMSI'])
  newdata2 <- redisltraj(na.omit(newdata), (7*60*60), type="time") #redisltraj(na.omit(newdata), 86400, type="time")
  res <- residenceTime(newdata2, radius = 50000, maxt=7, addinfo = TRUE,units="hour")
  for (i in 1:length(res)){#
    l <- lavielle(res[i], Lmin=2, Kmax=kmax, type="mean")
    seg<-chooseseg(l,draw = FALSE)
    fp<-findpath(l, segs,plotit = FALSE)
    for (j in 1:length(fp)){
      tmp<-ld(fp[j])
      if (nrow(tmp)>2)
        angle<-sliwinltr(fp[j], function(x) mean(cos(x$rel.angle)), type="locs", step=1,plotit=FALSE)
      else angle <- 1
      datestart <- as.POSIXct(strsplit(as.character(tmp$pkey), ".", fixed = TRUE)[[1]][2], format="%Y-%m-%d", tz=tz)
      dateend  <- as.POSIXct(strsplit(as.character(tmp$pkey), ".", fixed = TRUE)[[length(tmp$pkey)]][2], format="%Y-%m-%d", tz=tz)
      strburst<-as.character(tmp[1,'burst'])
      data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
             data$date >= datestart&
             data$date <= dateend,'period']<-
             replicate(nrow(data[as.character(data$MMSI) == as.character(tmp[1,'id'])&
					data$date >= datestart &
					data$date <= dateend,]), strburst)
      data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
             data$date > dateend, 'period'] <-
             		replicate(nrow(data[as.character(data$MMSI)==as.character(tmp[1,'id']) &
					data$date > dateend,]), strburst)
      if (typeof(angle)=='list')  {
        if (length(angle[[1]][!is.na(angle[[1]])])>0){
        if (median(angle[[1]][!is.na(angle[[1]])]) > (-0.8) && median(angle[[1]][!is.na(angle[[1]])]) < (0.8)){
          data<-tryCatch({
            data[as.character(data$MMSI) == as.character(tmp[1,'id'])&
                   data$period == strburst, 'movtype']<-'C'
            data
          },error=function(e){
            data[as.character(data$MMSI) == as.character(tmp[1,'id'])&
                   data$date >= datestart&
                   data$date <= dateend,'movtype']<-'C'
            data[as.character(data$MMSI) == as.character(tmp[1,'id'])&
                   data$date > dateend, 'movtype']<- 'C'
            data
          })
        }else{
          data<-tryCatch({
            data[as.character(data$MMSI) == as.character(tmp[1,'id'])&
                   data$period == strburst, 'movtype']<-'S'
            data
          },error=function(e){
            data[as.character(data$MMSI) == as.character(tmp[1,'id'])&
                   data$date >= datestart &
                   data$date <= dateend,'movtype']<-'S'
            data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
                   data$date>dateend, 'movtype']<- 'S'
            data
          })

        }
      }else {
        data<-tryCatch({
          data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
                 data$period==strburst, 'movtype']<-'C'
          data
        },error=function(e){
          data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
                 data$date>=datestart&
                 data$date<=dateend,'movtype']<-'C'
          data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
                 data$date>dateend, 'movtype']<- 'C'

          data

        })
      }
    }else{
      data<-tryCatch({
        data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
               data$period==strburst, 'movtype']<-'S'
        data
      },error=function(e){
        data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
               data$date>=datestart&
               data$date<=dateend,'movtype']<-'S'
        data[as.character(data$MMSI)==as.character(tmp[1,'id'])&
               data$date>dateend, 'movtype']<- 'S'

        data
      })
    }
   }
  }
  data1<-data[!is.na(data$period),]
  dframe<-data1
  return(dframe)
}


mmsi<-unique(data$MMSI)
cont<-1
for (i in mmsi){
  if (nrow(data[data$MMSI==i,])>1500){
  result<-longlinerpreds(data[data$MMSI==i,])
  if (cont==1){
    data1<-result
  }else{

        data1<-rbind(data1,result)

  }
  cont<-cont+1
  }

}
data1[,'preds']<-ifelse(data1$movtype=='S', 0, 1 )



data1[data1$distshore<11, 'preds']<-0
data1[data1$distshore<11, 'COARSE_FIS']<-0


write.csv(data1, file=outfile)

# table(factor(data1[,'preds'], levels=min(data1[,'COARSE_FIS']):max(data1[,'COARSE_FIS'])),factor(data1[,'COARSE_FIS'], levels=min(data1[,'COARSE_FIS']):max(data1[,'COARSE_FIS'])))
# sessionInfo()