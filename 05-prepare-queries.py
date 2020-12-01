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
    resp = requests.put(url=f"https://unit-test-api.{host}/queries/applications/{proj}/{flow}/{node}/{terminal}",
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
    "backendreq_id": f"//message/XMLNSC/{{{nsout}}}backendRequest/{{{nsout}}}invoiceId"
}
upload_queries(data, 'RequestMapping', 'out')

# UBL MAPPING IN
data = {
    "sap_documentNo": f"//SapTBkpf/BELNR",
    "sap_currencyId": f"//SapTBkpf/WAERS",
    "sap_documentDate": f"//SapTBkpf/BLDAT",
    "sap_orderNo": f"//SapTBsegHd/XREF1",
    "sap_customerReference": f"//SapTBsegHd/XREF2",
    "sap_customerNo": f"//SapTBsegHd/KUNNR",
    "sap_bookKey": f"//SapTBsegHd/BSCHL",
    "sap_paymentId": f"//SapTBsegHd/ZLSCH",
    "sap_taxableAmounts": f"//SapTBset//FWBAS",
    "sap_taxAmounts": f"//SapTBset//FWSTE",
    "sap_customerPostBox": f"//SapTKna1//PFACH",
    "sap_customerCity": f"//SapTKna1//ORT01",
    "sap_customerPostCode": f"//SapTKna1//PSTLZ",
    "sap_customerStreet": f"//SapTKna1//STRAS",
    "sap_customerCountry": f"//SapTKna1//LAND1",
}
upload_queries(data, 'UBLCompute', 'in')

# UBL MAPPING OUT
data = {
    "ubl_documentNo": f"//{{{invns}}}Invoice/{{{cbc}}}ID",
    "ubl_documentDate": f"//{{{invns}}}Invoice/{{{cbc}}}IssueDate",
    "ubl_orderNo": f"//{{{cac}}}OrderReference/{{{cbc}}}ID",
    "ubl_customerReference": f"//{{{cac}}}OrderReference/{{{cbc}}}CustomerReference",
    "ubl_customerNo": f"//{{{cac}}}AccountingCustomerParty/{{{cbc}}}SupplierAssignedAccountID"
}
upload_queries(data, 'UBLCompute', 'out')
