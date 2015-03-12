import random
from pymongo import MongoClient
from traffic_const import Const


class TestData:    

    def insertTestData(self,latitude,longitude):
        #6.914892, 79.972245 sliit location
        plat=latitude
        plon=longitude
        
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
        rawtraffic=db.rawtraffic
        
        t_lat=float(plat)
        t_lon=float(plon)
        
        for i in range(1,40000):
            appid="test_app"
            lat=random.uniform(t_lat-0.1,t_lat+0.1)
            lon=random.uniform(t_lon-0.1,t_lon+0.1)
            speed=random.randint(5,80)
            
            time=8.20
            date="2014-6-2"
            
            data={"appid":appid,
                  "location":[lat,lon],
                  "speed":speed,
                  "time":time,
                  "date":date,
                  "test-entry":i
                  }
            
            rawtraffic.insert(data)
            print(data)
            
