#!/usr/bin/env python
import requests
from argparse import ArgumentParser
from dnacentersdk import api
from dnacentersdk.exceptions import ApiError
import logging
import csv
import json
from  time import sleep, time
from dnac_config import DNAC, DNAC_USER, DNAC_PASSWORD
logger = logging.getLogger(__name__)

class TaskTimeoutError(Exception):
    pass

class TaskError(Exception):
    pass

class Task:
    def __init__(self,dnac, taskid):
        self.dnac = dnac
        self.taskid = taskid
    def wait_for_task(self, timeout=10,retry=1):
        start_time = time()
        first = True
        while True:
            result = dnac.task.get_task_by_id(self.taskid)

            if result.response.endTime is not None:
                return result
            else:
                # print a message the first time throu
                if first:
                    logger.debug("Task:{} not complete, waiting {} seconds, polling {}".format(self.taskid, timeout, retry))
                    first = False
                if timeout and (start_time + timeout < time()):
                    raise TaskTimeoutError("Task %s did not complete within the specified timeout "
                                           "(%s seconds)" % (self.taskid, timeout))

                logging.debug("Task=%s has not completed yet. Sleeping %s seconds..." % (self.taskid, retry))
                sleep(retry)
            if result.response.isError == "True":
                raise TaskError("Task {} had error {}".format(self.taskid, result.response.progress))
        return response

# need a template cache
class Template:
    def __init__(self, dnac, name):
        self.dnac = dnac
        self.name = name
        self.id, self.params = self.get_template_id(name)

    def get_template_id(self,name):
        templates = self.dnac.configuration_templates.gets_the_templates_available(project_names=["Onboarding Configuration"])

        versions  = [t.versionsInfo for t in templates if t.name == name]
        tids = [t.templateId for t in templates if t.name == name]
        logger.debug(versions)
        if versions == []:
            print("template:{} not found".format(name))
            return None, None
        version_cache  = { int(v.version): v.id for v in versions[0] }
        #tid  = version_cache[max(version_cache.keys())]
        tid = tids[0]
        rawparams = self.dnac.configuration_templates.get_template_details(tid)['templateParams']
        params = [r.parameterName for r in rawparams]

        return tid, params
    def validate_params(self, suppliedparams):
        missing = set(self.params) - set(suppliedparams)
        if missing != set ():
            print("missing vars:{}".format(missing))
        extra = set(suppliedparams) - set(self.params)
        if extra != set():
            #print("Extra vars:{}".format(extra))
            pass


class TemplateCache:
    def __init__(self,dnac):
        self.cache = {}
        self.dnac = dnac
    def add_template(self,name):
        template = Template(self.dnac, name)
        self.cache[name] = template
    def find_template(self,name):
        if name in self.cache:
            logger.debug("cach hit for {}".format(name))
            return self.cache[name]
        self.add_template(name)
        return self.cache[name]

class NewDevice:
    def __init__(self, dnac, name, serial, pid, template, vars):
        self.dnac = dnac
        self.name = name
        self.serial = serial
        self.pid = pid
        self.template = template
        self.vars = vars
        self.deviceid = None
    def update_deviceid(self,deviceid=None):
        if deviceid is not None:
            self.deviceid = deviceid
        else:
            result = self.dnac.device_onboarding_pnp.get_device_list(serial_number = self.serial)
            try:
                self.deviceid = result[0].id
            except IndexError as e:
                print("device not found")
            logger.info("found device id {} for existing device {}".format(self.deviceid, self.serial))
    def update_template(self, template):
        # usually when template is not found
        self.template = template

    def payload_to_add(self):
        payload = {
            "deviceInfo": {
                "hostname": self.name,
                "serialNumber": self.serial,
                "pid": self.pid,
                "sudiRequired": False,
                "userSudiSerialNos": [],
                "stack": False,
                "deviceType": "AccessPoint",
                "aaaCredentials": {
                    "username": "",
                    "password": ""
                }
            }
        }
        return payload
    def payload_to_claim(self, templateid):
        logger.debug("vars:{}".format(self.vars))
        payload = {
            "deviceId": self.deviceid,
            "hostname" : self.name,
            "configList": [
                {
                    "configId": templateid,
                    "configParameters":  [{'key' : k, 'value': v}   for k,v in self.vars.items() ]
                }
            ]

        }
        return(payload)

# need chunks of 10-20 devices.  add, then claim them
# a couple of states.
# added already, just claim.
# failed to add (serial number bad) dont claim.
# add and claim

class DeviceCache:
    def __init__(self):
        self.cache = {}
    def add_device(self, device):
        self.cache[device.serial] = device
    def all_devices(self):
        return self.cache.values()
    def find_device(self, serial):
        return self.cache[serial]

def get_devices(dnac, filename):
    device_cache = DeviceCache()
    f = open(filename, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            name = device_row.pop('name')
            serial = device_row.pop('serial')
            pid = device_row.pop('pid')
            template = device_row.pop('template')
            vars = device_row
            device_cache.add_device(NewDevice(dnac, name, serial, pid, template, vars))
    finally:
        f.close()
    return device_cache

def validate_templates(dnac, device_cache):
    template_cache = TemplateCache(dnac)
    for device in device_cache.all_devices():
        template = template_cache.find_template(device.template)
        logger.debug("template:{}. Params:{}".format(template.id, template.params))
        if template.id is None:
            print("removing template:{} from device:{}.  Template does not exist".format(template.name, device.serial))
            device_cache.find_device(device.serial).update_template(None)
            return
        supplied = device.vars.keys()
        template.validate_params(supplied)
    return template_cache

def add_devices(dnac, device_cache):
    payload = []
    for device in device_cache.all_devices():
        payload.append(device.payload_to_add())
    logger.info("PAY"+str(payload))

    # there is a limit of 1000 devices
    results = dnac.device_onboarding_pnp.import_devices_in_bulk(payload=payload)
    logger.debug("RE"+str(results))
    for res in results['successList']:
        serial = res['deviceInfo']['serialNumber']
        logger.debug("Serial:{}, id:{}".format(serial, res['id']))
        print("Added device: {}".format(serial))
        device_cache.find_device(res['deviceInfo']['serialNumber']).update_deviceid(res['id'])
    for res in results['failureList']:
        if "NCOB01019: Duplicate serial" in res.msg:
            device_cache.find_device(res.serialNum).update_deviceid()
            print("Device: {} already exists".format(res.serialNum))

def claim_devices(dnac, device_cache, template_cache):
    payloads = []
    bad_payload={
            "deviceId": "624160552ee4c1000b1bd24d",
            "configList": [
                {
                    "configId": "aaaa",
                    "configParameters":  [{'key' : 'k', 'value':' v'} ]
                }
            ]
        }
    # for testing
    #payload.append(bad_payload)
    for device in device_cache.all_devices():
        if device.template is None:
            logger.error("skipping device {} as no valid template found".format(device.serial))
            continue
        templateid = template_cache.find_template(device.template).id
        payloads.append(device.payload_to_claim(templateid))

    for payload in payloads:

        logger.info("payload for claim:{}".format(json.dumps(payload)))
        results = dnac.device_onboarding_pnp.claim_device( deviceClaimList=[payload],
                                                      populateInventory=True, configId=payload['configList'][0]['configId'])
        logger.info(results)
        if results.statusCode == 200:
            logger.info("all ok")
            mapping = {d.deviceid: d.serial for d in device_cache.all_devices()}

            print("claimed device:{}".format(mapping[payload['deviceId']]))


def main(dnac, filename):
    # modify this.
    # need to read input file. then batch up requests   Add/Claim in two steps.  The class should provide a method to crete the payload
    device_cache = get_devices(dnac, filename)
    template_cache = validate_templates(dnac, device_cache)
    added = add_devices(dnac,device_cache)
    claimed = claim_devices(dnac, device_cache, template_cache)

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
