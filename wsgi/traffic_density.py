
from pymongo import MongoClient
from traffic_const import Const
from pathfinder import Pathfinder

class TrafficDensity:

    def calculateDensity(self, plat,plon):
        
        lat=plat
        lon=plon
        
        result=[]
        
        t_lat=(float('{:.3f}'.format(lat)))
        t_lon=(float('{:.3f}'.format(lon)))
        for i in range(-3,3):
            t2_lat=t_lat+(i*0.002)
            
            for k in range(-3,3):
                t2_lon=t_lon+(k*0.002)
                
                client=MongoClient(Const.MONGODB_URL)
                db=client.trafficmonitor
                trafficdata= db.rawtraffic.find({"location": {"$within": {"$box": [[t2_lat, t2_lon], [t2_lat+0.002, t2_lon+0.002]]}}}).limit(500)
                
                count=0
                speed_sum=0
                traffic_temp={}
                
                for doc in trafficdata:    
                    speed_sum=speed_sum+doc["speed"] #5 should replace
                    count=count+1
                    
                if count>0:
                    traffic_temp={
                                  "avgspeed":speed_sum/count,
                                  "density":count,
                                  "location":[t2_lat,t2_lon],
                                  "roads":self.getRoadFragments(t2_lat,t2_lon)
                                  }
                    result.append(traffic_temp)
                
        #print result
        return result
    
    def getRoadFragments(self,lat,lon):
        
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
        roadset= db.roadFragments.find({"point": {"$within": {"$box": [[lat, lon], [lat+0.002, lon+0.002]]}}}).limit(500)
        roadlist=[]
        
        for row in roadset:
            roadlist.append(row["road"])
            
        if len(roadlist)==0:
            cell_width=0.002
            cell_height=0.002
            roadlist=Pathfinder().returnPathFragmentsOn(lat, lon, lat+cell_width, lon+cell_height);
            if len(roadlist)>0:
                for encodedpath in roadlist:
                    cellCenter=[lat+(cell_width/2), lon+(cell_height/2)]
                    db.roadFragments.insert({"point":cellCenter,
                          "road":encodedpath,
                          });
        return roadlist
        
#TrafficDensity().getRoadFragments(6.91532886,79.97250795)
#TrafficDensity().calculateDensity(6.91532886,79.97250795)
