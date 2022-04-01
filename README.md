# AP PnP Tool
This tool programmatical inserts AP in DNAC for Plug and Play (PnP)

It uses the new 2.3.2 API which allows an AP claim without a site assigment.

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

## Configuration file
The AP, the template and parameters need to be stored in a csv.  Some examples appear
in the data directory.

An example file
```
name,serial,pid,template,primaryWlcName,primaryWlcIP
bh-test-ap1,ABC2444LDK6,C9120AXI-Z,ap_json,wlc1,192.168.200.201
bh-test-ap2,ABC2444LD10,C9120AXI-Z,ap_json,wlc1,192.168.200.201
bh-test-ap3,ABC2444LD11,C9120AXI-Z,ap_json,wlc1,192.168.200.201

```

## Running


##