# AP PnP Tool
This tool programmatical inserts AP in DNAC for Plug and Play (PnP)

It uses the new 2.2.3 API which allows an AP claim without a site assigment.

Non-site based claim is important for use cases where DNA Center is not responsible for the configuration of the WLC

## Important Note.
The inital version of code did not set the pnp device type to AP.  This can cause issues with the PnP process if the PID is not a complete match.

If you provide an incomplete AP Product ID (PID) e.g (C9120 instead of C9120-AXE-A), then the device is added a a "default" type of device to PnP DB.

PnP process will try to discover the AP directly using SNMP, just like a normal device, which will fail.

The device type needs to be AP (or the PID a full match to the DNA Center PID DB).  The inital version of code would have resulted in the PnP process failing (even thought the AP was provisioned correctly, and associated to the WLC).

The code now forces the type to be AP,  the AP will be discovered via the WLC it associates to and added to the inventory, irrespective of the PID.

###June 2023:
In 2.3.3.x, need to have populateInventory=False, otherwise DNAC will try to discover the AP via SNMP, which will fail

## Getting stated
First (optional) step, create a vitualenv. This makes it less likely to clash with other python libraries in future.
Once the virtualenv is created, need to activate it.
```buildoutcfg
python3 -m venv env3
source env3/bin/activate
```

Next clone the code.

```buildoutcfg
git clone https://github.com/aradford123/DNAC-AP-PnP.git
```

Then install the  requirements (after upgrading pip). 
Older versions of pip may not install the requirements correctly.
```buildoutcfg
pip install -U pip
pip install -r requirements.txt
```


## Template
Template is required for the configuration.  Here is an example of a template with 
two parameters ($primaryWlcIP and $primaryWlcName).

```
{
"primaryWlcIP":"$primaryWlcIP",
"primaryWlcName":"$primaryWlcName",
"apGroup":"default-ap-group",
"apMode":"local"
} 
```

The full set of attributes are as follows:
```
{"primaryWlcIP":"PRI_WLC_IP",
 "primaryWlcName":"PRI_WLC_NAME",
 "secondaryWlcIP":"SEC_WLC_IP",
 "secondaryWlcName":"SEC_WLC_NAME",
 "tertiaryWlcIP":"TER_WLC_IP",
 "tertiaryWlcName":"TER_WLC_NAME",
 "policyTagName":"POLICY_TAG",
 "RFTagName":"RF_TAG",
 "siteTagName":"SITE_TAG",
 "apGroup":"AP_GRP",
 "apMode":"AP_MODE"
 }

```

It is possible to have a fixed template with no parameters
This template needs to be created in the Cisco DNA Center (tools->template editor)
Make sure you both save and commit it.

## AP Configuration file
The AP, the template and parameters need to be stored in a csv.  Some examples appear
in the data directory.

An example file
```
name,serial,pid,template,primaryWlcName,primaryWlcIP
bh-test-ap1,ABC2444LDK6,C9120AXI-Z,ap_json,wlc1,192.168.200.201
bh-test-ap2,ABC2444LD10,C9120AXI-Z,ap_json,wlc1,192.168.200.201
bh-test-ap3,ABC2444LD11,C9120AXI-Z,ap_json,wlc1,192.168.200.201

```

## Running the script

### Step 0: change the credential
You need to edit the dnac_config.py file to change the DNAC and user name and password.
If you know how to use environment variables, you can do that instead.

### Step 1: Create a template in DNAC
The template needs to be both saved and commited.

### Step 2: Create an AP configuration file
a csv simlar to the examples in the data directory.  Needs to contain, the name, serial, model, template and parameters 
for template (if any)

### Step 3: Run the script

```commandline
 ./add_pnp_ap.py data/test
Added device: ABC2444LDK6
Added device: ABC2444LD10
Added device: ABC2444LD11
claimed device:ABC2444LDK6
claimed device:ABC2444LD10
claimed device:ABC2444LD11

```

If the device already exists, that is fine, it will be claimed.


can also delete those AP using the del_ap script
```commandline
./del_ap.py data/test
Deleted: ABC2444LDK6
Deleted: ABC2444LD10
Deleted: ABC2444LD11

```

##
