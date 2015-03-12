
import sys
import pymongo
from traffic_const import Const
from pathfinder import Pathfinder
from pymongo import MongoClient,GEO2D
from test_data import TestData

args=sys.argv[1:]

if len(args)>0:
    command=args[0]
    
    if command=="create-index":
        if len(args)>1:
            table_name=args[1]
            if table_name=="rawtraffic":
                dbname=args[1]
                client=MongoClient(Const.MONGODB_URL)
                db=client.trafficmonitor
                results=db.rawtraffic.create_index([("location",GEO2D)])
                print "success"
            if table_name=="tempPointList":
                client=MongoClient(Const.MONGODB_URL)
                db=client.trafficmonitor
                results=db.tempPointsList.create_index([("point",GEO2D)])
                print "success"
            if table_name=="markersTB":
                client=MongoClient(Const.MONGODB_URL)
                db=client.trafficmonitor
                results=db.markersTB.create_index([("Location",GEO2D)])
                print "success"
            if table_name=="roadFragments":
                client=MongoClient(Const.MONGODB_URL)
                db=client.trafficmonitor
                results=db.roadFragments.create_index([("point",GEO2D)])
                print "success"
                    
        else:
            print "invalid args"
    if command=="find-pathfragments":
        if len(args)>4:
            s_lat=args[1]
            s_lon=args[2]
            e_lat=args[3]
            e_lon=args[4]
            Pathfinder().findPathFragmentsOn(s_lat,s_lon,e_lat,e_lon)
        else:
            print "using origin:malabe , destination:kaduwela"
            Pathfinder().findPathFragmentsOn(6.90391108,79.95521307,6.93586313,79.98426676)
            
    if command=="perform-gridoperation":
        print "performing grid operation"
        Pathfinder().performGridOperation()
    
    if command=="clear-table":
        if len(args)>1:
            table_name=args[1]
            if table_name=="rawtraffic":
                client=MongoClient(Const.MONGODB_URL)
                db=client.trafficmonitor
                db.rawtraffic.remove()
                print "rawtraffic table cleared"
                
            if table_name=="roadFragments":
                client=MongoClient(Const.MONGODB_URL)
                db=client.trafficmonitor
                db.roadFragments.remove()
                print "roadFragments table cleared"
                
    if command=="generate-testdata":
        if len(args)>2:
            s_lat=args[1]
            s_lon=args[2]
            print "generating random test traffic data using given location"
            TestData().insertTestData(s_lat,s_lon)
        else:
            print "using origin:sliit"
            TestData().insertTestData(6.914892, 79.972245)
        
    
    if command=="help":
        print "cbtms - application manage command list"
        print "\tcreate-index [table_name] : create a GEO2D index tables \n\t\t rawtraffic,tempPointList,markersTB,roadFragments"
        print "\tfind-pathfragments [s_lat] [s_lon] [e_lat] [e_lon] \n\t\t select location points from origin to destination"
        print "\tperform-gridopration :  taverse throug a conceptual grid \n\t\tand record road fragments"
        print "\tclear-table [table_name] : remove all data from db table \n\t\tex rawtraffic,roadFragments"
        print "\tgenerate-testdata [s_lat] [s_lon] : randomly generate and \n\t\tinsert test traffic data in sliit area"