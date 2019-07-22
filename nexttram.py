#!/usr/bin/env python3

import sys
import urllib.request
import urllib.parse
import json
import configparser
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

config = configparser.ConfigParser()

read_in = config.read(sys.argv[1])

assert read_in == [sys.argv[1]], read_in

base_uri = config['transportapi']['base_uri']
app_id = config['transportapi']['app_id']
app_key = config['transportapi']['app_key']
atcocode = config['main']['atcocode']

query = urllib.parse.urlencode({
    'app_id': app_id,
    'app_key': app_key,
    'group': 'no',
    'nextbuses': 'no'})
url = '{}/uk/bus/stop/{}/live.json?{}'.format(base_uri, atcocode, query)

log.debug('requesting API: %s', url)
req = urllib.request.Request(url)
req.add_header('User-Agent', 'NextTram/0.1')
req.add_header('Accept', 'application/json')

resp = urllib.request.urlopen(req)
resp = json.load(resp)

local_stop_name = resp['name']
departures = resp['departures']['all']
if not departures:
    log.info('No trams due')
log.info('Next tram from %s: %s to %s',
         local_stop_name,
         departures[0]['best_departure_estimate'],
         departures[0]['direction'])

