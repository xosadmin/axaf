import os,sys,subprocess
import ipaddress

def runCommand(cmd):
    run = subprocess.run(cmd,check=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = run.stdout.decode('utf-8')
    print(output)
    return output

def detectChain(head,chainName):
    try:
        runCommand([head,"-L",chainName])
        return True
    except:
        return False

def checkIP(ipaddr):
    bogon_addrs_v4 = [
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("169.254.0.0/16"),
        ipaddress.ip_network("0.0.0.0/8"),
        ipaddress.ip_network("224.0.0.0/4"),
    ]
    bogon_addrs_v6 = [
        ipaddress.ip_network("fc00::/7"),
        ipaddress.ip_network("::1/128"),
        ipaddress.ip_network("fe80::/10"),
        ipaddress.ip_network("::/128"),
        ipaddress.ip_network("ff00::/8"),
    ]
    try:
        network = ipaddress.ip_network(ipaddr, strict=False)
        if network.version == 4:
            for ip4 in bogon_addrs_v4:
                if network.overlaps(ip4):
                    print(f"Bogon IPv4 CIDR {ipaddr} detected. Ignored.")
                    return False
            if ipaddr != "0.0.0.0/0":
                return True
            else:
                return False
        elif network.version == 6:
            for ip6 in bogon_addrs_v6:
                if network.overlaps(ip6):
                    print(f"Bogon IPv6 CIDR {ipaddr} detected. Ignored.")
                    return False
            if ipaddr != "::/0" and ipaddr != "2000::/3":
                return True
            else:
                return False
    except:
        print(f"CIDR {ipaddr} is not a valid IPv4/IPv6 CIDR. Ignored.")
        return False
