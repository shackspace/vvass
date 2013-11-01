#!/usr/bin/python
#-*-coding:utf-8

from flask import Flask, abort, request, redirect, jsonify
import simplejson
import os
from urllib.request import urlopen

app = Flask(__name__)
app.config.update(Debug=True)

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
	get_EFA_from_VVS(stationID)
	return "ass"



def get_EFA_from_VVS(stationID):

	obj =  ("http://www2.vvs.de/vvs/widget/XML_DM_REQUEST?zocationServerActive=1&lsShowTrainsExplicit=1&stateless=1&language=de&SpEncId=0&anySigWhenPerfectNoOtherMatches=1&limit=20&depArr=departure&type_dm=any&anyObjFilter_dm=2&deleteAssignedStops=1&name_dm=5000082&mode=direct&dmLineSelectionAll=1&itdDateYear=2013&itdDateMonth=11&itdDateDay=12&itdTimeHour=19&itdTimeMinute=26&useRealtime=1")
	print(obj.getcode())

	return obj.getcode()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
