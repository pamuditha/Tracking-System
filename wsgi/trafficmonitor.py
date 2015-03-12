import os
import pymongo
import json
import time
import threading
import hashlib
import functools

from flask import Flask
from flask import request
from flask import jsonify
from flask import flash
from flask.templating import render_template
from flask.globals import session
from bson import json_util
from bson import objectid
from bson.son import SON
from pymongo import MongoClient,GEO2D
from json.decoder import JSONObject
from traffic_const import Const

from traffic_density import TrafficDensity
from test_data import TestData
from datetime import datetime,timedelta, date
from pathfinder import Pathfinder



app = Flask(__name__)
app.secret_key="mnsgmnsgmnsgmnsg"
TIMER_INTERVAL=60

#owner madhura
def timer():
    threading.Timer(TIMER_INTERVAL,timer).start()
    doInBackground()

#owner shared
def doInBackground():
    print (time.ctime()+" background processing")
    print bg_deletemarkers()
    test()
    
#owner madhura
def test():
    data = {"time":time.ctime()
           }
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    test=db.test
    #test.remove()
    regID=test.insert(data)

#owner sp
def bg_deletemarkers():
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    db.markersTB.remove({ "ExpiryTime":{ "$lt": datetime.now()} });
    
    return "removing expired markers"
    

#owner shared
@app.route("/")
def def_welcome():
    return "<h1>You are welcome to Community based Traffic Monitoring System</h1></br>"

#owner madhura
@app.route("/v2/retrievetraffic")
def def_retrieveTrafficv2():
    
    lat=float(request.args.get('lat'))
    lon=float(request.args.get('lon'))
    t_density=TrafficDensity()
    result=t_density.calculateDensity(lat,lon)
    return json.dumps({'results': list(result)}, default=json_util.default);

#owner madhura
@app.route("/v1/registerapp")
def def_registerApp():
    
    manufact = request.args.get('manufacturer')
    model=request.args.get('model')
    version=request.args.get('version')
    
    data = {"manufacturer":manufact,
           "model":model,
           "version":version
           }
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    regapps=db.registeredapps
    
    regID=regapps.insert(data)
    
    return jsonify(key=str(regID))

#owner madhura
@app.route("/v1/inserttraffic")
def def_insertTrafficData():
    
    appid=request.args.get('appid')
    lat=float(request.args.get('lat'))
    lon=float(request.args.get('lon'))
    speed=float(request.args.get('speed'))
    time=request.args.get('time')
    date=request.args.get('date')
    
    data={"appid":appid,
          "location":[lat,lon],
          "speed":speed,
          "time":time,
          "date":date}
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    radius=0.0062
    tbl_roadfragments=db.roadFragments
    roadfragmentslist= tbl_roadfragments.find({"point": SON([("$near", [lat, lon]), ("$maxDistance", radius)])}).limit(1)
    
    presult="rejected"
    if len(list(roadfragmentslist)):
        tbl_rawtraffic=db.rawtraffic
        rawTrafficId=tbl_rawtraffic.insert(data)
        presult="success"
    
    return jsonify(result=presult);

#owner madhura
@app.route("/v1/retrievetraffictemp")
def def_retrieveTraffictemp():
    
    appid=request.args.get('appid')
    lat=float(request.args.get('lat'))
    lon=float(request.args.get('lon'))
    time=request.args.get('time')
    date="2014-04-04"
    
    tempdata=[
              {
               "location":[6.914690,79.972212],
               "speed":15,
               "radius":500
               },
              {
               "location":[6.913183,79.972153],
               "speed":30,
               "radius":500
               },
              {
               "location":[6.917108,79.973407],
               "speed":60,
               "radius":500
               }
              ]
    return json.dumps({'results': list(tempdata)}, default=json_util.default);


#owner madhura
@app.route("/v1/retrievetraffic")
def def_retrieveTraffic():
    
    appid=request.args.get('appid')
    lat=float(request.args.get('lat'))
    lon=float(request.args.get('lon'))
    time=request.args.get('time')
    date="2014-04-04"
    radius=0.0062
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    trafficdata= db.rawtraffic.find({"location": SON([("$near", [lat, lon]), ("$maxDistance", radius)])}).limit(4)
    
    return json.dumps({'results': list(trafficdata)}, default=json_util.default);


#owner madhura
@app.route("/v1/retrievetrafficincircle")
def def_retrieveTrafficInCircle():
    
    appid=request.args.get('appid')
    lat=float(request.args.get('lat'))
    lon=float(request.args.get('lon'))
    time=request.args.get('time')
    date="2014-04-04"
    radius=0.0062
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    trafficdata=db.rawtraffic.find({"location": {"$within": {"$center": [[lat, lon], radius]}}})    
    return json.dumps({'results': list(trafficdata)}, default=json_util.default);


#owner sp
@app.route("/v1/retrievemarkers")
def def_retrievemarkers():
    
    Lat=float(request.args.get('lat'))
    Lon=float(request.args.get('lon'))
    radius=0.0062
    bg_deletemarkers()
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    markersdata= db.markersTB.find({"Location": SON([("$near", [Lat, Lon]), ("$maxDistance", radius)])})
    #markersdata=db.markersTB.find()
    
    return json.dumps({'results': list(markersdata)}, default=json_util.default);




#owner madhura
@app.route("/v1/removerawtraffic/<password>")
def def_removeDBrawtraffic(password):
    if password=="madmadhuramad":
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
    
        results=db.rawtraffic.remove()
        presult="success"
    else:
        presult="failed"
    return jsonify(result=presult);


#owner madhura
@app.route("/v1/createmongoindex/<password>")
def def_createGEOIndex(password):
    if password=="madmadhuramad":
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
    
        results=db.rawtraffic.create_index([("location",GEO2D)])
        presult="success"
    else:
        presult="failed"
    return jsonify(result=presult);

#owner madhura
@app.route("/v1/createmongoindex2/<password>")
def def_createGEOIndex2(password):
    if password=="madmadhuramad":
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
    
        results=db.tempPointsList.create_index([("point",GEO2D)])
        presult="success"
    else:
        presult="failed"
    return jsonify(result=presult);


#madhura
@app.route("/v1/viewalldata/<password>")
def def_viewAllData(password):
    if password=="madmadhuramad":
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
    
        alldata = results=db.rawtraffic.find()
        
    return json.dumps({'results': list(alldata)}, default=json_util.default);

#madhura
@app.route("/v1/inittestdata/<password>")
def def_initTestData(password):
    if password=="madmadhuramad":
        test=TestData()
        test.insertTestData()
    return json.dumps({'results': []}, default=json_util.default);

#codes for admin pannel

@app.route("/adminlogin",methods=['POST','GET'])
def def_adminLogin():
    
     client=MongoClient(Const.MONGODB_URL)
     db=client.trafficmonitor
     admintb=db.admindata
      
     if request.method =='POST':
        
        name1=request.form['login']
        password1=hashlib.sha224(request.form['password']).hexdigest()
        print(password1)
        result=db.admindata.find({"name":name1})
        noofcounts=result.count()
       
        print(result)

        if noofcounts==1 : 
          for k in result  :
            valuename=k["name"]
            
            valuepassword=k["password"]
            print(valuepassword)
          
            if name1 !=valuename or password1 !=valuepassword :
                 flash("Error in Username or Password")
            else :
                 session['login']=name1
                 return render_template('index.html',name1=name1)
        else:
            flash("Error in Username or Password")
                          
     return render_template('login.html')


def login_required(method):

 @functools.wraps(method)
 def wrapper(*args, **kwargs):
  if 'login' in session:
  
    return method(*args, **kwargs)
  
  else:
    flash("A login is required to see the page!")
    return render_template('login.html')
 return wrapper


@app.route("/register",methods=['POST','GET'])
@login_required
def def_register():
     client=MongoClient(Const.MONGODB_URL)
     db=client.trafficmonitor
     admintb=db.admindata
    
     if request.method =='POST':
         
         name=request.form['name']
         
         password=hashlib.sha224(request.form['password']).hexdigest()
         print(password)
         confirmpassword=request.form['confirm']
         phonenumber=request.form['tel']
         email=request.form['email']
        
         numberofrows=db.admindata.find({"name" : name}).count()
         rowsforemail=db.admindata.find({"email" : email}).count()
         rowsforphonenumber=db.admindata.find({"pnumber" : phonenumber}).count()
         print(numberofrows)
         
         if numberofrows>0 :
             
             flash("Error in Adding ! User already exist")
             
         else :
             
             if rowsforphonenumber>0:
                  
                 flash("Error in Adding ! Phone number already exist")
             else:
                 if rowsforemail >0:
                     flash("Error in Adding ! Email already exist")
                     
                 else:
                   data={"name":name,
                        "password":password,
                        "pnumber":phonenumber,
                        "email":email
                        }
                   value= admintb.insert(data)
                   print(value)
                   flash("Successfully Added")
         
     return render_template('register.html')



@app.route("/update",methods=['POST','GET'])
@login_required
def def_update():
    
     client=MongoClient(Const.MONGODB_URL)
     db=client.trafficmonitor
     admintb=db.admindata
     
     if request.method =='POST':
         
         passvaluename= session['login']
         newpasspassvalue=list(db.admindata.find({"name": passvaluename}))
         
         name1=request.form['name']
         password=hashlib.sha224(request.form['password']).hexdigest()
         confirmpassword=request.form['confirm']
         phonenumber=request.form['tel']
         email=request.form['email']
         
         
         number=db.admindata.find({"name" : name1}).count()
         number1=db.admindata.find({"name" : name1})
         numberofemail=db.admindata.find({"email" : email}).count()
         numberofphonenumber=db.admindata.find({"pnumber" : phonenumber}).count()
        
         print "before check number if"
         print(number)
         if number>0 :
             for row in number1:
                currentnumber=row['pnumber']
                currentemail=row['email']
                print "cnumber"
                print (currentemail)
                print (currentnumber)
                    
                if numberofphonenumber>0 and currentnumber!=phonenumber: 
                        flash("Error in Updating ! Phone number already exist")
                        return render_template('Update.html',newpasspassvalue=newpasspassvalue)   
                else:
                    if numberofemail>0 and currentemail !=email:
                        flash("Error in Updating ! Email already exist")
                        
                        return render_template('Update.html',newpasspassvalue=newpasspassvalue)           
                    else:
                        #if name1 in loggedin:
                        value= db.admindata.update( {"name": name1},{ "$set": {"password": password,"pnumber":phonenumber,"email": email}});
                        print(value)
                        flash("Successfully Updated")
                        passvaluename= session['login']
         
                        newpasspassvalue=list(db.admindata.find({"name": passvaluename}))
                        return render_template('Update.html',newpasspassvalue=newpasspassvalue)
         else :
               flash("Error in Updating ! User not exist")
         
     else:
         passvaluename= session['login']
         
         newpasspassvalue=list(db.admindata.find({"name": passvaluename}))
                   
         return render_template('Update.html',newpasspassvalue=newpasspassvalue)


@app.route("/view",methods=['POST','GET'])
@login_required
def def_load():
    
     client=MongoClient(Const.MONGODB_URL)
     db=client.trafficmonitor
     admintb=db.admindata
     
     if request.method =='POST':
        mydata1=list(db.admindata.find())      
        return render_template('view.html',mydata=mydata1)
     else:
        mydata=list(db.admindata.find())
        print(mydata)
                 
        return render_template('view.html',mydata=mydata)


@app.route("/delete",methods=['POST','GET'])
def def_delete():
    
     client=MongoClient(Const.MONGODB_URL)
     db=client.trafficmonitor
     admintb=db.admindata
     
     if request.method =='POST':
    
       print"before newdata" 
       
       nametodelete=request.form['tag']
       if nametodelete == 'Madmin' :
           
         print("nametodelete")
        
         return json.dumps({'results': 'error'}, default=json_util.default);
     
       else:

         print(nametodelete)
          
         deletedata=db.admindata.remove({"name" :nametodelete})
         response=list(deletedata)
       
         return json.dumps({'results': response}, default=json_util.default);
     else:
         print"In side else"


@app.route("/v1/getraffic", methods=['POST','GET'])
def load_ajax():   
    if request.method =='GET':
        checked_Date=request.args.get('chkdate');
        print checked_Date
        
        client=MongoClient(Const.MONGODB_URL)
        db=client.bar_test
        bar_test2= db.bar_test.find({"Date" :checked_Date});
        bardata=list(bar_test2)
        print bardata
        
        return json.dumps({'results': bardata}, default=json_util.default);

@app.route("/adminpanel/modelcounts")
def countmodels():
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    key = ["model"]
    condition = {}
    initial = { "count": 0 }
    reduce = 'function(doc, out) { out.count++;}'
    
    modelcount = db.registeredapps.group(key,condition,initial,reduce)
    tot_modelcount=list(modelcount)
        
    return json.dumps({'totresults':tot_modelcount}, default=json_util.default);


@app.route("/adminpanel/trafficbydate", methods=['POST','GET'])
def trafficdatewise():

    if request.method =='GET': 
        Lat=float(request.args.get('lat'))
        Lon=float(request.args.get('lon'))
        
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    trafficdata=db.rawdata

    radius=0.005
     
    key = [ "date" ]
    condition = {"location": SON([("$near", [Lat, Lon]), ("$maxDistance", radius)])}
    #condition = {}
    initial = { "count": 0 }
    reduce = 'function(doc, out) { out.count++;}'
    
    trafficbydate = trafficdata.group(key,condition,initial,reduce)
    traffic=list(trafficbydate)
    
    print traffic
       
    return json.dumps({'result_dateByTraffic':traffic}, default=json_util.default);

    
#============================================ By  Gihan========================================


@app.route("/adminpanel/trafficfindbydatetime", methods=['POST','GET'])
def trafficfindbydateandtime():

    if request.method =='GET': 
        lat=float(request.args.get('lat'))
        lon=float(request.args.get('lon'))
        startDate=request.args.get('startdate')
        endDate=request.args.get('enddate')
    
    
    startFindtrafficdate=startDate.split("T")[0]
    startFindtraffictime=startDate.split("T")[1]
    endFindtrafficdate=endDate.split("T")[0]
    endFindtraffictime=endDate.split("T")[1]
    
    print startFindtrafficdate
    print endFindtrafficdate
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    trafficdata=db.rawdata

    radius=0.005
     
    key = [ "date" ]
    condition = {'date':{'$gte':startFindtrafficdate,'$lte':endFindtrafficdate},'time':{'$gte':startFindtraffictime,'$lte':endFindtraffictime}}
    initial = { "count": 0 }
    reduce = 'function(doc, out) { out.count++;}' 
     
    trafficbydate = trafficdata.group(key,condition,initial,reduce)
    traffic=list(trafficbydate)
    
    print traffic
       
    return json.dumps({'result_dateByTraffic':traffic}, default=json_util.default);



#==================================================================================    
    

    
#owner SP
@app.route('/markersCALL', methods=["POST", "GET"])
def load_markers_ajax(): 
    if request.method =='GET':
        lat=float(request.args.get('lat'))
        lon=float(request.args.get('lon'))
        markerID = 0
        markerID=int(request.args.get('markerid'))
        print markerID
        radius=float(request.args.get('radius'))
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
        
        if lat==0 and lon==0:
            markersdata = db.markersTB.find({"Marker":markerID})
        
        elif markerID ==0 and radius ==0:
            markersdata = db.markersTB.find({"Location": [lat, lon]})
            
        elif radius ==0:
            markersdata = db.markersTB.find({ "$and" :[{"Location": [lat, lon]},{"Marker":markerID}]})
            
        elif markerID ==0:
            markersdata= db.markersTB.find({"Location": SON([("$near", [lat, lon]), ("$maxDistance", radius)])})
            
        else:
            markersdata= db.markersTB.find({ "$and" :[{"Location": [("$near", [lat, lon]), ("$maxDistance", radius)]}, {"Marker":markerID}]})
        #markersdata= db.markersTB.find({'Marker':markerID})
        markersdatalist=list(markersdata)
        print {'results': markersdatalist}
       
        
        return json.dumps({'results':markersdatalist}, default=json_util.default);


#owner SP
@app.route('/deviceDataCALL', methods=["POST", "GET"])
def load_devices_ajax():
   
 
    if request.method =='GET':
        manu = request.args.get('manu')
        model = request.args.get('model')
        ver = request.args.get('ver')

        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
             
        if manu=='' and  model=='': 
            devicedata= db.registeredapps.find({"version":ver})
            
        elif manu=='' and  ver=='': 
            devicedata= db.registeredapps.find({"model": model})
            
        elif model=='' and  ver=='':  
            devicedata= db.registeredapps.find({"manufacturer":manu})
           
        elif manu=='' :
            devicedata= db.registeredapps.find({"$and" :[{"model": model},{"version":ver}]})
            
        elif model=='' : 
            devicedata= db.registeredapps.find({"$and" :[{"manufacturer": manu},{"version":ver}]})
           
        elif ver=='' :
            devicedata= db.registeredapps.find({"$and" :[{"model": model},{"manufacturer":manu}]})
            
        else:     
            devicedata= db.registeredapps.find({"$and" :[{"manufacturer": manu},{"model": model},{"version":ver}]})
            print '666666'
        
        devicedatalist=list(devicedata)
        print {'results': devicedatalist}
              
        return json.dumps({'results':devicedatalist}, default=json_util.default);


#owner sp
@app.route("/v1/insertmarkers")
def def_insertmarkers():

    Lat=float(request.args.get('lat'))
    Lon=float(request.args.get('lon'))
    markerID=int(request.args.get('markerid'))+1
    if markerID == 1:
        expirytime = datetime.now()+ timedelta( minutes = 5)
       
    elif markerID == 2:
        expirytime = datetime.now()+ timedelta( minutes = 1)
       
    elif markerID == 3:
        expirytime = datetime.now()+ timedelta( minutes = 5)
   
    elif markerID == 4:
        expirytime = datetime.now()+ timedelta( minutes = 20)
    
    presult="failed"
    if markerID<=4:
       
        data={"Location":[Lat,Lon],
              "Marker":markerID,
              "ExpiryTime":expirytime,
              }
        
        client=MongoClient(Const.MONGODB_URL)
        db=client.trafficmonitor
        markers=db.markersTB
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    markers=db.markersTB
    
    radius=0.0015
    
    markersaround= markers.find({"Location": SON([("$near", [Lat, Lon]), ("$maxDistance", radius)]),"Marker":markerID}).count()
    
    if markersaround>0:
         existingmarker= db.markersTB.find({"Location": SON([("$near", [Lat, Lon]), ("$maxDistance", radius)]),"Marker":markerID})
         id=0
         
         for doc in existingmarker:
             id=doc["_id"]
             
         markers.update( { "_id" : id },{ "$set" : { "ExpiryTime" : expirytime } })      
         presult="rejected"
        
    else :   
         markers.insert(data) 
         presult="success"
        
    print presult
    return jsonify(result=presult);


#owner sp
@app.route("/v1/deletemarkers")
def deletemarkers():
    
    Lat=float(request.args.get('lat'))
    Lon=float(request.args.get('lon'))
    markerID=int(request.args.get('markerid'))+1
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    presult="failed"
    
    marker = db.markersTB.find({ "$and" :[{"Location": [Lat, Lon]},{"Marker":markerID}]}).count()
    
    if marker>0:    
        db.markersTB.remove({ "$and" :[{"Location": [Lat, Lon]},{"Marker":markerID}]});
        presult="success"
    
    print presult
    return jsonify(result=presult);

@app.route("/adminpanel/loadtraffic")
def def_loadTraffic():
 
    client=MongoClient('Const.MONGODB_URL')
    db=client.trafficmonitor
    
    trafficdata= db.rawtraffic.find().limit(10)
    
    return json.dumps({'results': list(trafficdata)}, default=json_util.default);
   

@app.route("/adminpanel/markerstatictics")
def def_markerstat():
    
 
    Lat=float(request.args.get('lat'))
    Lon=float(request.args.get('lon'))
    markerID=int(request.args.get('markerid'))
    
    newLat= "%.1f" % Lat
    newLon= "%.1f" % Lon
    
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    Locexist= db.markerstat.find({"Location":[newLat,newLon]}).count()
    
    if Locexist >0:

        
        if markerID == 1:
        
            db.markerstat.update({"Location":[newLat,newLon]},{ "$inc":{"CarAccident":1}})
        
        elif markerID == 2:
            
            db.markerstat.update({"Location":[newLat,newLon]},{ "$inc":{"Police":1}})
            
        elif markerID == 3:
            
            db.markerstat.update({"Location":[newLat,newLon]},{ "$inc":{"TrafficCamera":1}})
            
        elif markerID == 4:
            
            db.markerstat.update({"Location":[newLat,newLon]},{ "$inc":{"TreeDown":1}})
        
    else:
        
        data={"Location":[newLat,newLon],
              "CarAccident":0,
              "Police":0,
              "TrafficCamera":0,
              "TreeDown":0,
              }
        
        db.markerstat.insert(data)        
    return 'success'





@app.route("/adminpanel/loadmarkerstatictics")
def def_loadmarkerstat():
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    markerstats= db.markerstat.find()
    
    return json.dumps({'results': list(markerstats)}, default=json_util.default);


#madhura
@app.route("/adminpanel/getroutelist",methods=['POST','GET'])
def def_getRouteList():
    sLat=float(request.args.get('slat'))
    sLon=float(request.args.get('slon'))
    eLat=float(request.args.get('elat'))
    eLon=float(request.args.get('elon'))
    pathlist=Pathfinder().returnPathFragmentsOn(sLat, sLon,eLat, eLon)
    return json.dumps({'results': pathlist}, default=json_util.default)


#madhura
@app.route("/v1/getroute")
def def_getRoute():
    myLines = [
               {
                    "coordinates": [[6.9149, 79.97219], [6.9158, 79.97186], [6.91618, 79.97032],[6.91765, 79.96802]]
                },
                {
                    "coordinates": [[6.91573, 79.96538], [6.91388, 79.96583], [6.91228, 79.96609]]
                }
               ]
    return json.dumps({'results': list(myLines)}, default=json_util.default)

#madhura
@app.route("/adminpanel/getmarkers",methods=['POST','GET'])
def def_foradminpanel_getmarkers():
    Lat=float(request.args.get('lat'))
    Lon=float(request.args.get('lon'))
    radius=0.01
    
    bg_deletemarkers()
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    markersdata= db.markersTB.find({"Location": SON([("$near", [Lat, Lon]), ("$maxDistance", radius)])})
    return json.dumps({'results': list(markersdata)}, default=json_util.default);

#madhura
@app.route("/adminpanel/gettrafficdensity",methods=['POST','GET'])
def def_gettrafficdensity():
    sLat=float(request.args.get('slat'))
    sLon=float(request.args.get('slon'))
    eLat=float(request.args.get('elat'))
    eLon=float(request.args.get('elon'))
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    result=[]
    
    box_width=eLat-sLat
    iterations=0
    if box_width<0 : box_width=box_width*-1
    if box_width>0.2 : iterations=int(box_width/0.1)
    if box_width>0.02 : iterations=int(box_width/0.01)
    if box_width>0.004 : iterations=int(box_width/0.004)
    radius=box_width/iterations
    print iterations
    print radius
    for i in range(0,iterations+1):
        lat=sLat+radius*2*i
        for k in range(0,iterations+1):
            lon=sLon+radius*2*k
            #trafficdata= db.rawtraffic.find({"location": {"$within": {"$center": [[lat, lon], radius]}}})
            key = []
            condition = {"location": {"$within": {"$center": [[lat, lon], radius]}}}
            initial = { "count": 0 }
            reduce = 'function(doc, out) { out.count++;}'
            trafficdata = db.rawtraffic.group(key,condition,initial,reduce)
            for row in trafficdata:
                result_elem={
                              "density":row['count'],
                              "location":[lat,lon]
                              }
                print result_elem
                print row
                result.append(result_elem)
        #print result
    return json.dumps({'results': list(result)}, default=json_util.default);


#forecasting  section

@app.route("/adminpanel/forecastbyexpontial", methods=['POST','GET'])
def  def_trafficforecastingexponetial():
     
    
    if request.method =='GET':
         
        Lat= float(request.args.get('lat'))
        Lon= float(request.args.get('lon'))
        
        #print Lat
        #print Lon 
        
      
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
   
    
    trafficdata=db.rawdata
     

    radius=0.005
     
    key = [ "date" ]
    condition = {}
    condition = {"location": SON([("$near", [Lat, Lon]), ("$maxDistance", radius)])}
    
    initial = { "count": 0 }
    reduce = 'function(doc, out) { out.count++;}'
    
    trafficbydate = trafficdata.group(key,condition,initial,reduce)
    traffic=list(trafficbydate)
    
    print trafficdata
    
    #=========================Expotinal Alogrithem===============================================
    
    data_index=0
    forecastvalue=0;
    perviousforcat=0
    alpha=0.2
    data_read_index=0
    data_values=[]
    date_values=[]
    forecast_contanier=[]
    
    for data_element in trafficbydate:
        data_values.append(data_element['count'])
        date_values.append(data_element['date'])
         
    for data_index,(data_element1,data_element2) in  enumerate(zip(data_values,date_values)):
        if(data_index == 0): 
           forecastvalue=data_values[data_index]
           perviousforcat=forecastvalue
           forecastTempFirst={
                               "orginalcount":data_values[data_index], 
                               "forecast":forecastvalue,
                               "forecastDate":date_values[data_index]
                               
                              }
           forecast_contanier.append(forecastTempFirst)
        
        if(data_index > 0):       
        #forecastvalue=forecastvalue+0.2*(data[data_index]-forecastvalue)
          forecastvalue=0.2*data_values[data_index-1] +(1-0.2)*perviousforcat
          perviousforcat=forecastvalue
          forecastTempOther={
                             "orginalcount":data_values[data_index],
                             "forecast":forecastvalue,
                             "forecastDate":date_values[data_index]
                            
                            }
          forecast_contanier.append(forecastTempOther)
          #print  forecastvalue
         
          
    #next day forecasting
    forecastvalue=0.2*data_values[data_index] +(1-0.2)*perviousforcat
    
     
    
    d =datetime.strptime(date_values[data_index], "%Y-%m-%d")
    delta =timedelta(days=1)
    d += delta
    print d.strftime("%Y-%m-%d")
  
    forecastNext={
                        "forecast":forecastvalue,
                       "forecastDate":d.strftime("%Y-%m-%d")
                            
                  }
    forecast_contanier.append(forecastNext)
             
    #======================================================
 

 
    
  
  

    
    
    
    
    
    
    print forecast_contanier
    
   
    return json.dumps({'result_forecast':forecast_contanier}, default=json_util.default);


@app.route("/adminpanel/forecastbyholt", methods=['POST','GET'])
def  def_trafficforecastingbyHoltmethod():

 
    if request.method =='GET':
         
        Lat=float(request.args.get('lat'))
        Lon=float(request.args.get('lon'))
        forecastingDays=int(request.args.get('countday'))
        
        print Lat
        print Lon 
        print forecastingDays
     
    
    client=MongoClient(Const.MONGODB_URL)
    db=client.trafficmonitor
    
    trafficdata=db.rawdata
    
     
    radius=0.005
     
    key = [ "date" ]
    condition = {}
    condition = {"location": SON([("$near", [Lat, Lon]), ("$maxDistance", radius)])}
    
    initial = { "count": 0 }
    reduce = 'function(doc, out) { out.count++;}'
    
    trafficbydate = trafficdata.group(key,condition,initial,reduce)
    traffic=list(trafficbydate)
    
    #================Implementing  Holt Method==========================
    base=0
    trend=0
    alpha=0.2
    beeta=0.1
    previousbase=0
    prvioustrend=0
    smothing=0
    
    
    
    data_index=0
    data_values=[]
    date_values=[]
    forecast_contanier=[]
    
    for data_element in trafficbydate:
        data_values.append(data_element['count'])
        date_values.append(data_element['date'])
         
    for data_index,(data_element1,data_element2) in  enumerate(zip(data_values,date_values)):
        if(data_index == 0): 
           base=data_values[data_index]
           previousbase=base
           prvioustrend=trend
           
           firstdeafultvalue={
                        "trafficcount":data_values[data_index],
                       "forecastDate":date_values[data_index]
                            
                  }
           forecast_contanier.append(firstdeafultvalue)
         
        
        if(data_index > 0):       
           base=alpha*data_values[data_index-1]+(1-alpha)*base
          # print base
           trend=beeta*(base-previousbase)+(1-beeta)*trend
           
           smothing=prvioustrend+previousbase
           
           print smothing
           
           forecastwithsmothing={
                        "trafficcount":data_values[data_index],
                        "forecastDate":date_values[data_index],
                        "smothingValue":smothing
                            
                  }
           forecast_contanier.append(forecastwithsmothing)
           
           previousbase=base
           prvioustrend=trend
        
         
          
    #next days/month forecasting
    no_of_day=1
    nextforcatvalue=0
    lastday=datetime.strptime(date_values[data_index], "%Y-%m-%d")
    delta =timedelta(days=1)
    
    while(no_of_day <= forecastingDays):
      #print nextforcatvalue
      nextforcatvalue=previousbase+no_of_day*prvioustrend
      lastday += delta
      
      forecastNext={
                        "smothingValue":nextforcatvalue,
                       "forecastDate":lastday.strftime("%Y-%m-%d")
                            
                  }
      forecast_contanier.append(forecastNext)
      no_of_day += 1
    
    
    #======================================================
 
 
    print forecast_contanier
    
   
    return json.dumps({'result_forecastbyholt':forecast_contanier}, default=json_util.default);


    
if __name__ == "__main__":
    #timer()
    app.run(debug=True,use_reloader=False)

