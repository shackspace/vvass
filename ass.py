#!/usr/bin/python
#-*-coding: utf-8 -*-

from flask import Flask, abort, request, redirect, jsonify, Response
import json
import simplejson
import http.cookiejar
import urllib.request
import time
import xml.etree.ElementTree as ET

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/station/<int:stationId>")
def stationId(stationId=None):
    if stationId is None:
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
    if isinstance(parsed, Response):
        return parsed
    else:
        return Response(parsed, content_type='application/json; charset=utf-8')


def get_EFA_from_VVS(stationId):
    """send HTTP Request to VVS and return a xml string"""
    #parameters needed for EFA
    zocationServerActive = 1
    lsShowTrainsExplicit = 1
    stateless = 1
    language = 'de'
    SpEncId = 0
    anySigWhenPerfectNoOtherMatches = 1
    #max amount of arrivals to be returned
    limit = 5
    depArr = 'departure'
    type_dm = 'any'
    anyObjFilter_dm = 2
    deleteAssignedStops = 1
    name_dm = stationId
    mode = 'direct'
    dmLineSelectionAll = 1
    itdDateYear = int(time.strftime('%y'))
    itdDateMonth = int(time.strftime('%m'))
    itdDateDay = int(time.strftime('%d'))
    itdTimeHour = int(time.strftime('%H'))
    itdTimeMinute = int(time.strftime('%M'))
    useRealtime = 1

    url = 'http://www2.vvs.de/vvs/widget/XML_DM_REQUEST?'
    url += 'zocationServerActive=%d' % zocationServerActive
    url += '&lsShowTrainsExplicit%d' % lsShowTrainsExplicit
    url += '&stateless=%d' % stateless
    url += '&language=%s' % language
    url += '&SpEncId=%d' % SpEncId
    url += '&anySigWhenPerfectNoOtherMatches=%d'\
        % anySigWhenPerfectNoOtherMatches
    url += '&limit=%d' % limit
    url += '&depArr=%s' % depArr
    url += '&type_dm=%s' % type_dm
    url += '&anyObjFilter_dm=%d' % anyObjFilter_dm
    url += '&deleteAssignedStops=%d' % deleteAssignedStops
    url += '&name_dm=%s' % name_dm
    url += '&mode=%s' % mode
    url += '&dmLineSelectionAll=%d' % dmLineSelectionAll
    url += '&itdDateYear=%d' % itdDateYear
    url += '&itdDateMonth=%d' % itdDateMonth
    url += '&itdDateDay=%d' % itdDateDay
    url += '&itdTimeHour=%d' % itdTimeHour
    url += '&itdTimeMinute=%d' % itdTimeMinute
    url += '&useRealtime=%d' % useRealtime

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.
                                         HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent',
                          'Mozilla/5.0 (X11; Linux x86_64; rv:22.0)'
                          'Gecko/20100101 Firefox/22.0')]
    opener.addheaders = [('Accept-Charset', 'utf-8')]
    efa = opener.open(url)
    data = efa.read()
    #debugging informaton
    code = efa.getcode()
    efa.close()

    if code != 200:
        return "ERROR"

    return(data)


def parseEFA(efa):
    """receive efa data and return a json object"""
    root = ET.fromstring(efa)
    xmlDepartures = root.findall('./itdDepartureMonitorRequest/'
                                 + 'itdDepartureList/itdDeparture')
    if len(xmlDepartures) == 0:
        return jsonify(
            status='error',
            message='The EFA presented an empty itdDepartureList. Reason therefore might be an unknown station ID.')

    departures = []

    for departure in xmlDepartures:
        stopName = departure.attrib['stopName']
        itdServingLine = departure.find('itdServingLine')
        symbol = itdServingLine.attrib['symbol']
        direction = itdServingLine.attrib['direction']
        itdDate = departure.find('itdDateTime/itdDate')
        year = itdDate.attrib['year']
        month = fixdate(itdDate.attrib['month'])
        day = fixdate(itdDate.attrib['day'])
        itdTime = departure.find('itdDateTime/itdTime')
        hour = fixdate(itdTime.attrib['hour'])
        minute = fixdate(itdTime.attrib['minute'])
        #yyyymmddHHMM
        departureTime = year + month + day + hour + minute
        route = departure.find('itdServingLine/itdRouteDescText').text

        ret = {'stopName': stopName,
               'symbol': symbol,
               'direction': direction,
               'departureTime': departureTime,
               'route': route}

        departures.append(ret)

    requestTime = timestr = time.strftime('%Y%m%d%H%M')
    dataset = {'status': 'success',
               'requestTime': requestTime,
               'departures': departures}
    response = json.dumps(dataset, indent=4,
                          separators=(',', ': '),
                          ensure_ascii=False)
    return response


def fixdate(date):
    """ fixes single digit date characters with a leading 0
"""
    if len(date) != 2:
        date = '0' + date
    return date


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
