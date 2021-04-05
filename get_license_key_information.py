#!/usr/bin/pyhon3
#
#  Juniper output for rpc.get function obtaining:
#  > show system license keys | display xml rpc
#

from jnpr.junos import Device
from lxml import etree
import jxmlease

username = 'login'
password = 'passwd'

def sys_license_keys(host):
   dev = Device(host=host, user=username, password=password, normalize=True)
   dev.open()

   rpc = dev.rpc.get_license_key_information()
   rpc_xml = etree.tostring(rpc, pretty_print=True, encoding='unicode')
   dev.close()

   xmlparser = jxmlease.Parser()
   result = jxmlease.parse(rpc_xml)
   print('\n' + 120 * '*' + '\n')
   print('License keys for host {}'.format(host))
   print('\n' + 120 * '*' + '\n')

# if license exists
   if result.get('license-key-information'):
       # For multiple licenses
       if isinstance(result['license-key-information']['license-key'],list):
           for license in result['license-key-information']['license-key']:
               print(license['key-data'])
       # For a single license
       else:
           print(result['license-key-information']['license-key']['key-data'])

# if no license
   else:
       print('No license found')

hosts = [
'X.X.X.X',
'Y.Y.Y.Y'
]

for host in hosts:
   try:
     sys_license_keys(host)
   except:
     print('Something went wrong connecting to host {}'.format(host))
