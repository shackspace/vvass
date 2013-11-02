#!/usr/bin/python
#-*-coding:utf-8

from flask import Flask, abort, request, redirect, jsonify
import simplejson
import os
from urllib.request import urlopen

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
    itdDateYear=2012
    itdDateMonth=10
    itdDateDay=12
    itdTimeHour=19
    itdTimeMinute=26
    useRealtime=1

    efa = urlopen('http://www2.vvs.de/vvs/widget/XML_DM_REQUEST?\
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
    print('requested URL %s:' % efa.geturl())
    print('return code: %d' % efa.getcode())
    print(efa.read())
    return "foo" 

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
