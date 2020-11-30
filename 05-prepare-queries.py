import requests
import sys
import json

# INTERFACE data
proj = 'FICO27_B2BInvoice_Demo'
flow = 'FICO27_B2BInvoice'

# NAMESPACES
nsin = 'inputns'
nsout = 'outputns'
sapns = 'http://www.ibm.com/xmlns/prod/websphere/j2ca/sap/sapzfib2btriggerinvoicewrapper'
invns = 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
cbc = 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
cac = 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'

host = sys.argv[1]
auth = requests.auth.HTTPBasicAuth("user1", "pw1")


def upload_queries(payload, node, terminal):
    print(payload)
    print(node, terminal)
    resp = requests.post(url=f"https://unit-test-api.{host}/queries/applications/{proj}/{flow}/{node}/{terminal}",
                         data=json.dumps(payload).encode('utf-8'), auth=auth)
    print(resp.status_code)
    if resp.status_code < 300:
        print(json.loads(resp.content))
    print()


# REQUEST MAPPING IN
data = {
    "in_id": f"//message/XMLNSC/{{{nsin}}}serviceRequest/{{{nsin}}}id"
}
upload_queries(data, 'RequestMapping', 'in')

# REQUEST MAPPING OUT
data = {
    "backend_id": f"//message/XMLNSC/{{{nsout}}}backendRequest/{{{nsout}}}invoiceId"
}
upload_queries(data, 'RequestMapping', 'out')

# UBL MAPPING IN
data = {
    
}

# UBL MAPPING OUT


