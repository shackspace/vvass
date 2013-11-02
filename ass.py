#!/usr/bin/python
#-*-coding: utf-8 -*-

from flask import Flask, abort, request, redirect, jsonify
import simplejson
import http.cookiejar, urllib.request
#from urllib.request import urlopen
import time
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/station/<int:stationId>")
def stationId(stationId=None):
    if stationId == None:
        return jsonify(
            status="error",
            message="please specify a station ID!"
            )
    
    if len(str(stationId)) != 7:
        return jsonify(
            status="error",
            message="the station ID needs to be a 7 digit integer"
            )
    efa = get_EFA_from_VVS(stationId)

    if efa == "ERROR":
        return jsonify(
            status="error",
            message="Couldn't connect to the EFA, something is broken."
            )

    parsed = parseEFA(efa)
    
    return "aww yiss"



def get_EFA_from_VVS(stationId):
    print('station ID: %d' % stationId)
    ##parameters needed for EFA
    zocationServerActive=1
    lsShowTrainsExplicit=1
    stateless=1
    language='de'
    SpEncId=0
    anySigWhenPerfectNoOtherMatches=1
    #max amount of arrivals to be returned
    limit=5
    depArr='departure'
    type_dm='any'
    anyObjFilter_dm=2
    deleteAssignedStops=1
    name_dm=stationId
    mode='direct'
    dmLineSelectionAll=1
    itdDateYear=int(time.strftime('%y'))
    itdDateMonth=int(time.strftime('%m'))
    itdDateDay=int(time.strftime('%d'))
    itdTimeHour=int(time.strftime('%H'))
    itdTimeMinute=int(time.strftime('%M'))
    useRealtime=1

    url = ('http://www2.vvs.de/vvs/widget/XML_DM_REQUEST?\
zocationServerActive=%d\
&lsShowTrainsExplicit%d\
&stateless=%d\
&language=%s\
&SpEncId=%d\
&anySigWhenPerfectNoOtherMatches=%d\
&limit=%d\
&depArr=%s\
&type_dm=%s\
&anyObjFilter_dm=%d\
&deleteAssignedStops=%d\
&name_dm=%s\
&mode=%s\
&dmLineSelectionAll=%d\
&itdDateYear=%d\
&itdDateMonth=%d\
&itdDateDay=%d\
&itdTimeHour=%d\
&itdTimeMinute=%d\
&useRealtime=%d' % (zocationServerActive, lsShowTrainsExplicit,stateless,language,SpEncId,anySigWhenPerfectNoOtherMatches,limit,depArr,type_dm, anyObjFilter_dm, deleteAssignedStops, name_dm, mode, dmLineSelectionAll, itdDateYear, itdDateMonth, itdDateDay, itdTimeHour, itdTimeMinute, useRealtime))

    
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0')]
    efa = opener.open(url)
    data = efa.read()
    #debugging informaton
    code = efa.getcode()
    efa.close()
    
    print('requested URL %s:' % url)
    print('return code: %d' % code) 
    if code != 200:
        return "ERROR"

    return(data)

def parseEFA(efa):
    root = ET.fromstring(efa)
    xmlDepartures = root.findall('./itdDepartureMonitorRequest/itdDepartureList/itdDeparture')
    #TODO: wenn keine departures da sind fehler schmeissen
    for departure in xmlDepartures:
        stopName = departure.attrib['stopName']
        itdServingLine = departure.find('itdServingLine')
        symbol = itdServingLine.attrib['symbol']
        destination = itdServingLine.attrib['direction']
        route = departure.find('itdServingLine/itdRouteDescText').text
        print(stopName)
        print(symbol + "  " + destination)
        print(route)
        print("----------------------------------------")



if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
