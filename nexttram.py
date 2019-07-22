#!/usr/bin/env python3

import sys
import json
import logging
import argparse
import configparser
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

class NextTram:
    def __init__(self, configfilename):
        config = configparser.ConfigParser()

        read_in = config.read(configfilename)
        if read_in != [configfilename]:
            log.error('Unable to read config file at %s', configfilename)
            raise IOError(
                'Unable to read config file at {}'.format(configfilename))

        self.base_uri = config['transportapi']['base_uri']
        self.app_id = config['transportapi']['app_id']
        self.app_key = config['transportapi']['app_key']
        self.atcocode = config['main']['atcocode']

    def __call__(self):
        query = urllib.parse.urlencode({
            'app_id': self.app_id,
            'app_key': self.app_key,
            'group': 'no',
            'nextbuses': 'no'})
        url = '{}/uk/bus/stop/{}/live.json?{}'.format(
            self.base_uri, self.atcocode, query)

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
        return local_stop_name, departures[0]


def main(args):
    parser = argparse.ArgumentParser(description='Display the next tram')
    parser.add_argument('configfile', help='Path to the config file')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args(args[1:])

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    nexttram = NextTram(args.configfile)
    stop_name, departure_details = nexttram()
    print('Next tram from {}: {} to {}'.format(
        stop_name,
        departure_details['best_departure_estimate'],
        departure_details['direction']))


if __name__ == '__main__':
    sys.exit(main(sys.argv))

