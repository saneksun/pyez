#!/usr/bin/pyhon3

from jnpr.junos import Device
from lxml import etree
from datetime import datetime
import jxmlease
import os, csv, re

username = 'username'
password = 'password'

def sys_hardware(host,inv):
   dev = Device(host=host, user=username, password=password, normalize=True)
   dev.open()
   hostname=str(dev.facts['hostname'])
   print('Connecting to {} \n'.format(hostname))
   rpc = dev.rpc.get_chassis_inventory()
   rpc_xml = etree.tostring(rpc, pretty_print=True, encoding='unicode')
   dev.close()

   xmlparser = jxmlease.Parser()
   result = jxmlease.parse(rpc_xml)
   chassis_type=str(result['chassis-inventory']['chassis']['description'])

   if any('chassis-sub-module' in modules for modules in result['chassis-inventory']['chassis']['chassis-module']):
       for modules in result['chassis-inventory']['chassis']['chassis-module']:
           if re.match(r'Routing Engine \d', str(modules.get('name'))) is None:
               inv.append(hostname+','+chassis_type+','+str(modules['model-number']+','+str(modules['name'])+','+str(modules['serial-number'])))
           if modules.get('chassis-sub-module'):
               for submodules in modules.get('chassis-sub-module'):
                   if submodules.get('chassis-sub-sub-module'):
                       for items in submodules.get('chassis-sub-sub-module'):
                           inv.append(hostname+','+chassis_type+','+str(items['description'])+','+str(items['name'])+','+str(items['serial-number']))

                   elif submodules.get('serial-number') and str(submodules.get('serial-number')) != 'BUILTIN':
                       if any(str(submodules.get('serial-number')) in invent for invent in inv):
                           continue
                       else:
                           inv.append(hostname+','+chassis_type+','+str(submodules['model-number'])+','+str(submodules['name'])+','+str(submodules['serial-number']))

   else:
       inv.append(hostname+','+chassis_type+','+str(result['chassis-inventory']['chassis'].get('description'))+','
               +str(result['chassis-inventory']['chassis'].get('description'))+','
               +str(result['chassis-inventory']['chassis'].get('serial-number')))
   return(inv)

hosts = [
'X.X.X.X',
'Y.Y.Y.Y'
]
inv=[]

for host in hosts:
   try:
     sys_hardware(host,inv)
   except:
     print('Something went wrong connecting to host {}'.format(host))

with open('network_inventory.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([datetime.now().isoformat(timespec='minutes')])
    writer.writerow(['Hostname', 'Chassis type','Model', 'Name', 'Serial number'])
    for line in inv:
        writer.writerow([line])
