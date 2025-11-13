import os,sys
import configparser,re
import util
from ezipset import ezIPSet
import rpki

def prefixGen(asset,inet):
    inet = inet.lower()
    iplist = []
    flag = ""
    if inet == "ipv4":
        flag = "-4"
    elif inet == "ipv6":
        flag = "-6"
    else:
        return False
    cmd = ["bgpq4",flag,"-F","%n/%l\n",asset]
    returns = util.runCommand(cmd)
    for line in returns.splitlines():
        if line.strip() == "\n":
            continue # Skip empty line
        if util.checkIP(line):
            iplist.append(line)
    return iplist

def addFirewall(header, chainName, ipsetName, allowDeny):
    action = ""

    if allowDeny:
        action = "ACCEPT"
    else:
        action = "DROP"

    if util.detectChain(header,chainName):
        clearcmd = [
            [header, "-F", chainName],
            [header, "-D", "FORWARD", "-j", chainName],
            [header, "-X", chainName]]
        for cc in clearcmd:
            util.runCommand(cc)
    # Clear existing rules

    cmd = [[header,"-N",chainName],
           [header,"-A","FORWARD", "-j", chainName],
           [header, "-A", chainName, "-m", "set", "--match-set", ipsetName, "src", "-j", action],
           [header, "-A", chainName, "-m", "set", "--match-set", ipsetName, "dst", "-j", action]]

    for item in cmd:
        util.runCommand(item)

def addIPSet(iplist, ipsetname, inet, asn=None):
    ipset = ezIPSet(raise_on_errors=False)
    inetConvert = ""
    
    if inet == "ipv4":
        inetConvert = "inet"
    elif inet == "ipv6":
        inetConvert = "inet6"
    else:
        return False

    try:
        ipset.destroy_set(ipsetname)
        print(f"IPset {ipsetname} destroyed successfully.")
    except Exception as e:
        print(f"Error destroying IPset {ipsetname}: {str(e)}")
    
    try:
        ipset.create_set(ipsetname, set_type="hash:net", family=inetConvert, ignore_if_exists=True)
        print(f"IPset {ipsetname} created successfully.")
    except Exception as e:
        print(f"Error creating IPset {ipsetname}: {str(e)}")
        return False

    for ip in iplist:
        if util.checkIP(ip):
            try:
                if ifEnableRPKIValid and (not rpki.checkPrefix(asn,ip) or asn is None):
                    print(f"{ip} will not be added because of rpki verify error.")
                    continue
                ipset.add_entry(ipsetname, ip)
                print(f"Added IP {ip} to {ipsetname}.")
            except Exception as e:
                print(f"Error adding IP {ip} to {ipsetname}: {str(e)}")


print(f"Welcome to AX AS-SET Filter.")

if not os.path.exists(os.path.join("config.ini")):
    print(f"Cannot find configure file. Exiting...")
    sys.exit(1)

config = configparser.ConfigParser()
config.read(os.path.join("config.ini"))

ifEnableRPKIValid = config.getboolean(section="rpki_verify",option="enable",fallback=False)

settings = {}
util.runCommand(["iptables","-P", "FORWARD", "DROP"])
util.runCommand(["ip6tables","-P", "FORWARD", "DROP"])

for section in config.sections():
    if section == "rpki_verify":
        continue

    try:
        asset = config.get(section,"asset")
        inet = config.get(section,"inet")
        forward = config.getboolean(section,"forward")
        asn = config.get(section,"asn",fallback=None)
    except Exception as e:
        print(f"The config {section} is missing asset, inet or forward. Skipping...")
        continue

    if forward is None:
        ifForward = True
    else:
        ifForward = forward

    if not asset or not inet:
        print(f"The configuration {section} is missing. Skipping.")
        continue

    if ifEnableRPKIValid and not util.checkASN(asn):
        print(f"The ASN is invalid. Skipping configure...")
        continue

    settings[section] = {
        "asset": asset.lower(),
        "inet": inet.lower(),
        "forward": ifForward,
        "asn": asn
    }

for key, value in settings.items():
    asset = value["asset"]
    inet = value["inet"]
    ifForward = value["forward"]
    asn = value["asn"]

    if inet == "ipv4":
        header = "iptables"
    elif inet == "ipv6":
        header = "ip6tables"
    else:
        print(f"The inet for {asset} is not IPv4 or IPv6. Skipped.")
        continue

    chainName = f"{key}_FW"
    ipsetName = f"{key}_NN"

    prefixList = prefixGen(asset,inet)
    if not prefixList:
        print(f"The prefix list is empty or invalid AS-Set. Skipping...")
        continue

    addIPSet(prefixList,ipsetName,inet,asn)
    print(f"Prefix List has been written to IPset.")

    addFirewall(header,chainName,ipsetName,ifForward)
    print(f"Firewall rules for {asset} have been added.")

print("Complete.")