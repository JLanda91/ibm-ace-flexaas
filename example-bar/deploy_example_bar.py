import requests
import sys
import os


bar_file = "FICO27_B2BInvoice_Demo.bar"
f = open(bar_file, "rb")
binary = f.read()
f.close()
url = f'https://{sys.argv[1]}/apiv2/deploy'
print(f"Deploying {bar_file} to ACE integration server ...{os.linesep}")
response = requests.post(url,
                         data=binary,
                         auth=requests.auth.HTTPBasicAuth('admin1', 'admin1'),
                         headers={'Content-Type': 'application/octet-stream'})
print(response.status_code, response.content)
