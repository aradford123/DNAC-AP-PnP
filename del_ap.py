#!/usr/bin/env python
import requests
from argparse import ArgumentParser
from dnacentersdk import api
from dnacentersdk.exceptions import ApiError
import logging
import csv
from  time import sleep, time
from dnac_config import DNAC, DNAC_USER, DNAC_PASSWORD
logger = logging.getLogger(__name__)

def main(dnac, filename):

    f = open(filename, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            serial = device_row.pop('serial')
            # find it, then delete it
            result = dnac.device_onboarding_pnp.get_device_list(serial_number=serial)
            try:
                deviceid =  result[0].id
            except IndexError as e:
                print("device: {} not found".format(serial))
                continue
            result = dnac.device_onboarding_pnp.delete_device_by_id_from_pnp(id=deviceid)
            if 'deviceInfo' in result:
                print("Deleted: {}".format(serial))
            else:
                print("Error deleting:{}:{}".format(serial, json.dumps(result)))
    finally:
        f.close()

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument('devices', type=str,
                        help='device inventory csv file')
    parser.add_argument('-v', action='store_true',
                        help="verbose")
    args = parser.parse_args()

    if args.v:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.debug("logging enabled")
    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    dnac = api.DNACenterAPI(base_url='https://{}:443'.format(DNAC),
                                username=DNAC_USER,password=DNAC_PASSWORD,verify=False)
    main(dnac, filename=args.devices)