import requests
from util import checkASN, checkIP

def decomposeReturn(returns):
    try:
        outputs = {
            "result": returns["validated_route"]["validity"]["state"],
            "detail": returns["validated_route"]["validity"]["description"]
        }
    except KeyError as e:
        print(f"Missing expected key in response data: {e}")
        return None
    return outputs

def checkPrefix(asn,prefix):
    if "AS" in asn.upper():
        asn = asn.replace("AS","")
    print(f"Validating {prefix} with ASN {asn}")
    try:
        prefixMask = int(prefix.split("/")[1])
        if prefixMask > 48:
            print(f"Prefix mask is too big or it's an bogon prefix. Ignored.")
            return False
    except:
        print(f"Invalid prefix: {prefix}")
        return False

    if checkASN(asn) and checkIP(prefix.split("/")[0]):
        try:
            rrdp_url = f"https://rpki-validator.ripe.net/validity?asn={asn}&prefix={prefix}"
            response = requests.get(rrdp_url)
            if response.status_code == 200:
                respdata = response.json()
                respdecomp = decomposeReturn(respdata)
                if respdecomp is not None:
                    if respdecomp["result"] == "valid":
                        print(f"RPKI validation successful.")
                        return True
                    else:
                        print(f"The RPKI record for prefix {prefix} is invalid. Reason: {respdecomp['detail']}")
                        return False
                else:
                    print("Issue while decomposing data.")
                    return False
            else:
                print(f"RRDP Request failed with error code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Request Failed: {str(e)}")
            return False
    else:
        print("Invalid or bogon ASN detected.")
        return False