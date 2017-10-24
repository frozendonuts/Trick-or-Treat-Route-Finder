import urllib
import simplejson 
from pprint import pprint
import re
import gmplot
import random
import numpy
import csv
from configure import key


#Get list of addresses from CSV file and put into format for API
AL = []

with open('Neighborhood_Data.csv', 'rb') as addressData:
    reader = csv.reader(addressData, delimiter='\t', quotechar='|')
    
    for row in reader:
        s = '+'.join(row)
        AL.append(s.replace(' ','+'))


#remove html tags from API data
def removeTags(raw_html):
    
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext    
    
    
#takes in list of addresses and returns a string for the request
def setWaypoints(addressesList):

    s = ''
    for i in xrange(len(addressesList)):
        s = s + '|' + addressesList[i]
    return s


# just randomly pick houses to visit
r = random.randint(0,len(AL)-1)

origin_return = AL[r]
AL.pop(r)

addresses = numpy.random.choice(AL,20,replace=False)


#returns in a threeple (list of instructions, lat and long of route steps, lat and long of houses, lat and long for plotting deadends)
def findRoute(origin, addresses,key):

    baseURL = 'https://maps.googleapis.com/maps/api/directions/json?'

    mode = 'walking'

    request = baseURL + 'origin=' + origin_return + '&destination=' + origin_return + '&waypoints=optimize:true' + setWaypoints(addresses)+'&mode='+mode+'&key='+key
    result =  simplejson.load(urllib.urlopen(request))

    instructions = []
    latStep = []
    longStep = []

    latLeg = []
    longLeg = []

    latDead = []
    longDead = []

    for i in xrange(len(result['routes'][0]['legs'])):

        latStep.append(result['routes'][0]['legs'][i]['steps'][0]["start_location"]['lat'])
        longStep.append(result['routes'][0]['legs'][i]['steps'][0]["start_location"]['lng'])
        instructions.append(removeTags(result['routes'][0]['legs'][i]['steps'][0]["html_instructions"]))
        
        for j in xrange(1,len(result['routes'][0]['legs'][i]['steps'])):
        
        
            instructions.append(removeTags(result['routes'][0]['legs'][i]['steps'][j]["html_instructions"]))
            
            lat_curr = result['routes'][0]['legs'][i]['steps'][j]["start_location"]['lat']
            long_curr = result['routes'][0]['legs'][i]['steps'][j]["start_location"]['lng']

            
            if lat_curr in latStep and result['routes'][0]['legs'][i]['steps'][j-1].has_key("maneuver") == 0:
            
                latDead.append(latStep[latStep.index(lat_curr):])
                latStep = latStep[:latStep.index(lat_curr)+1]
            
                longDead.append(longStep[latStep.index(lat_curr):])
                longStep = longStep[:latStep.index(lat_curr)+1]          
            
            else:
                
                latStep.append(lat_curr)
                longStep.append(long_curr)
            
    
        latLeg.append(result['routes'][0]['legs'][i]["end_location"]['lat'])
        longLeg.append(result['routes'][0]['legs'][i]["end_location"]['lng'])
        
    
    latStep.append(latStep[0])
    longStep.append(longStep[0])


    return instructions, latStep, longStep, latLeg, longLeg, latDead, longDead   


#makes the google map and highlights the route    
def makePlot(latStep, longStep, latLeg, longLeg, latDead, longDead):
    
    gmap = gmplot.GoogleMapPlotter(49.236494, -123.143997, 16)

    gmap.plot(latStep, longStep, 'cornflowerblue', edge_width=5)
    
    for i in xrange(len(latDead)):
        gmap.plot(latDead[i], longDead[i], 'cornflowerblue', edge_width=5)

    gmap.scatter(latLeg[0:-1], longLeg[0:-1], '#3B0B39', size=7.5, marker=False)
    a = [latLeg[-1],latLeg[-1]]
    b = [longLeg[-1],longLeg[-1]]
    gmap.scatter(a, b, '#e53c16', size=5, marker=False)
    gmap.draw("route.html")
    

(a,b,c,d,e,f,g) = findRoute(origin_return,addresses,key)

directions = '<br><br>'.join(a)

makePlot(b,c,d,e,f,g)



badLines = ["""<body style="margin:0px; padding:0px;" onload="initialize()">\n""", """\t<div id="map_canvas" style="width: 100%; height: 100%;"></div>\n"""]
goodLines = ["""<body style="margin:50px; padding:50px;" onload="initialize()">\n""", """\t<div id="map_canvas" style="width: 50%; height: 100%;"></div>\n"""]


f = open('route.html','r')

lines = f.readlines()
       
f.close()

for i in xrange(len(lines)):
    if badLines[0] == lines[i]:
        lines[i] = goodLines[0]
    if badLines[1] == lines[i]:
        lines[i] = goodLines[1]


stuff = ["""\n<div id="map_canvas" style="width: 50%; height: 100%;"></div>\n""", """<div style="Position: absolute; top:50px; left:700px;">\n""", '<p style="font-size:12px"; font-family:helvetica;>' + directions + '</p>\n', """</div>\n"""]

newlines = lines[:-2] + stuff + lines[-2:]

f = open('route.html','w')

for i in xrange(len(newlines)):
    f.write(newlines[i])
    
f.close()

