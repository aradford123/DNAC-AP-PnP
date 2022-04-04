# AP PnP Tool
This tool programmatical inserts AP in DNAC for Plug and Play (PnP)

It uses the new 2.2.3 API which allows an AP claim without a site assigment.

Non-site based claim is important for use cases where DNA Center is not responsible for the configuration of the WLC

## Installing

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

It is possible to have a fixed template with no parameters

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