
import  urllib
import json
from pymongo import MongoClient
from polyline_encoder import GoogleEncoder
from traffic_const import Const

class Pathfinder:

    def findPathFragmentsOn(self, s_lat,s_lon,e_lat,e_lon):
        slat=str(s_lat)
        slon=str(s_lon)
        elan=str(e_lat)
        elon=str(e_lon)
        url='http://maps.googleapis.com/maps/api/directions/json?origin='+slat+","+slon+'&destination='+elan+','+elon+'&sensor=false&units=metric&mode=driving'
        
        output=json.load(urllib.urlopen(url))
        
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
        pointsList=db.tempPointsList
        pointsList.remove()
        
        for route in output['routes']:
            for leg in route['legs']:
                for step in leg['steps']:
                    polyline=step['polyline']
                    points=polyline['points']
                    #print points
                    pointslist=GoogleEncoder.decode(points)
                    
                    for latlg in pointslist:
                        pointsList.insert({"point":[latlg[1],latlg[0]]})
                        print latlg
    
    
    
    def returnPathFragmentsOn(self, s_lat,s_lon,e_lat,e_lon):
        slat=str(s_lat)
        slon=str(s_lon)
        elan=str(e_lat)
        elon=str(e_lon)
        url='http://maps.googleapis.com/maps/api/directions/json?origin='+slat+","+slon+'&destination='+elan+','+elon+'&sensor=false&units=metric&mode=driving'
        
        output=json.load(urllib.urlopen(url))
        
        #client=MongoClient(Const.MONGODB_URL)
        #db=client.trafficmonitor
        #pointsList=db.tempPointsList
        #pointsList.remove()
        
        encordedPathList=[]
        
        for route in output['routes']:
            for leg in route['legs']:
                for step in leg['steps']:
                    polyline=step['polyline']
                    points=polyline['points']
                    encordedPathList.append(points)
        return encordedPathList



    
    def performGridOperation(self):
        
        lat=6.91532886
        lon=79.97250795
        
        cell_width=0.002
        cell_height=0.002
        
        result=[]
        
        t_lat=(float('{:.3f}'.format(lat)))
        t_lon=(float('{:.3f}'.format(lon)))
        
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
        tbl_pointslist=db.tempPointsList
        tbl_roadfragments=db.roadFragments
        
        for i in range(-100,100):
            t2_lat=t_lat+(i*cell_width)
            
            for i in range(-100,100):
                t2_lon=t_lon+(i*cell_height)
                
                trafficdata= tbl_pointslist.find({"point": {"$within": {"$box": [[t2_lat, t2_lon], [t2_lat+cell_width, t2_lon+cell_height]]}}}).limit(1000)
                
                pointsInCell=list()
                for row in trafficdata:
                    pointsInCell.append((row['point'][0],row['point'][1]))
                
                if len(pointsInCell)>0:
                    road_encoded=GoogleEncoder.encode_coords(pointsInCell)
                    cellCenter=[t2_lat+(cell_width/2), t2_lon+(cell_height/2)]
                    
                    data={"point":cellCenter,
                          "road":road_encoded,
                          }
                    tbl_roadfragments.insert(data)
                    print road_encoded,cellCenter
        
        
        
#Pathfinder().findPathFragmentsOn(6.90391108,79.95521307,6.93586313,79.98426676)
#Pathfinder().performGridOperation()

