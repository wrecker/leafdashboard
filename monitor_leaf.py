#!/usr/bin/python

import datetime
import re
import requests
import sha
import sys
import time
import xmltodict
from pytz import timezone

__author__ = 'Mahesh Raju <coder@mahesh.net>'
__version__ = '0.1.0'
__license__ = 'MIT'


PASSWORD_FILE = ".leafpasswd"
DATE_FMT = "%Y-%m-%d %H:%M:%S %Z%z"

## STRING TEMPLATES ##
# North America
BASE_URL = "https://nissan-na-smartphone-biz.viaaq.com/aqPortal/smartphoneProxy"
USER_URL = "%s/userService" % BASE_URL
VEHICLE_URL = "%s/vehicleService" % BASE_URL

LOGIN_TMPL = """
<?xml version="1.0" encoding="UTF-8"?>
<ns2:SmartphoneLoginWithAdditionalOperationRequest xmlns:ns2="urn:com:airbiquity:smartphone.userservices:v1">
  <SmartphoneOperationType>SmartphoneLatestBatteryStatusRequest</SmartphoneOperationType>
  <SmartphoneLoginInfo>
    <UUID>%s</UUID>
    <Locale>US</Locale>
    <UserLoginInfo>
      <userId>%s</userId>
      <userPassword>%s</userPassword>
    </UserLoginInfo>
    <AppVersion>2.3.2</AppVersion>
    <SmartphoneType>ANDROID</SmartphoneType>
    <DeviceToken>DUMMY%s</DeviceToken>
  </SmartphoneLoginInfo>
</ns2:SmartphoneLoginWithAdditionalOperationRequest>
"""[1:-1]

BATTERY_CHECK_TMPL = """
<?xml version="1.0" encoding="UTF-8"?>
<ns4:SmartphoneRemoteBatteryStatusCheckRequest xmlns:ns4="urn:com:airbiquity:smartphone.vehicleservice:v1" xmlns:ns2="urn:com:hitachi:gdc:type:portalcommon:v1" xmlns:ns3="urn:com:hitachi:gdc:type:vehicle:v1">
  <ns3:BatteryStatusCheckRequest>
    <ns3:VehicleServiceRequestHeader>
      <ns2:VIN>%s</ns2:VIN>
    </ns3:VehicleServiceRequestHeader>
  </ns3:BatteryStatusCheckRequest>
</ns4:SmartphoneRemoteBatteryStatusCheckRequest>
"""[1:-1]

BATTERY_STATUS_TMPL = """
<?xml version="1.0" encoding="UTF-8"?>
<ns2:SmartphoneGetVehicleInfoRequest xmlns:ns2="urn:com:airbiquity:smartphone.userservices:v1">
  <SmartphoneOperationType>SmartphoneLatestBatteryStatusRequest</SmartphoneOperationType>
  <changeVehicle>false</changeVehicle>
  <VehicleInfo>
    <Vin>%s</Vin>
  </VehicleInfo>
</ns2:SmartphoneGetVehicleInfoRequest>
"""[1:-1]


def get_status(OUT_FILE):
    with open(PASSWORD_FILE) as f:
        credentials = [x.strip().split(':') for x in f.readlines()]
    USERNAME, PASSWORD = credentials[0]

    session = requests.Session()
    headers = { 'Content-Type': 'text/xml', 
                'User-Agent': 'NissanLEAF/1.40 CFNetwork/485.13.9 Darwin/11.0.0 pyCW' }

    login_xml = LOGIN_TMPL % (sha.sha("leaf_monitor:%s" % USERNAME).hexdigest(),
                              USERNAME, PASSWORD, time.time())

    req = session.post(USER_URL, headers = headers, data = login_xml, verify = False)
    if req.status_code != 200:
        print "Login to Carwings Failed: Response Code %d / Content: %s" % (req.status_code, req.content)
        sys.exit(1)

    data = xmltodict.parse(req.content)
    if 'ns7:SmartphoneErrorType' in data:
        print "Login to Carwings Failed: Received Error / Content: %s" % (req.content)

    vin = data['ns2:SmartphoneLoginWithAdditionalOperationResponse']\
              ['ns4:SmartphoneLatestBatteryStatusResponse']\
              ['SmartphoneBatteryStatusResponseType']['VehicleInfo']['Vin']
    req.close()

    # Send a request to update vehicle stats
    req = session.post(VEHICLE_URL, headers = headers,
                       data = BATTERY_CHECK_TMPL % vin, verify = False)
    if req.status_code != 200:
        print ("Carwings Request to update stats failed: Response Code %d "
               "/ Content: %s") % (req.status_code, req.content)
        sys.exit(1)
    req.close()

    time.sleep(20)
    retry = 3
    req = None
    while retry > 0:
        try:
            req = session.post(USER_URL, headers = headers,
                               data = BATTERY_STATUS_TMPL % vin, verify = False)
        except Exception, e:
            print "Bad Status code: %s" % e
            retry -= 1
            if retry == 0:
                sys.exit(1)
            time.sleep(5)
        else:
            break

    data = xmltodict.parse(req.content)
    response = data['ns2:SmartphoneGetVehicleInfoResponse']\
                  ['ns4:SmartphoneLatestBatteryStatusResponse']\
                  ['SmartphoneBatteryStatusResponseType']
    status = response['ns3:BatteryStatusRecords']

    s = response['lastBatteryStatusCheckExecutionTime']
    d = datetime.datetime(*map(int, re.split('[^\d]', s)[:-1])).replace(tzinfo=timezone('UTC'))
    last_update_date = d.astimezone(timezone('US/Pacific')).strftime(DATE_FMT)

    range_ac_on = int(int(status['ns3:CruisingRangeAcOn']) * 0.0006213)
    range_ac_off = int(int(status['ns3:CruisingRangeAcOff']) * 0.0006213)
    connected = 'NO'
    if status['ns3:PluginState'] == 'CONNECTED':
        connected = 'YES'
    charging = 'NO'
    if status['ns3:BatteryStatus']['ns3:BatteryChargingStatus'] == 'NORMAL_CHARGING':
        charging = 'YES'
    charge_left = status['ns3:BatteryStatus']['ns3:BatteryRemainingAmount']

    print '%s | %s | %s | %s | %s @ %s' % (range_ac_on, range_ac_off, connected, charging,
                                           charge_left, last_update_date)
    with open(OUT_FILE, 'w') as OUT:
        OUT.write(('{"rangeAcOn": %d, "rangeAcOff": %d,'
                   '"charging": "%s", "pluggedIn": "%s", "batteryLevel": %s, '
                   '"lastUpdate": "%s"}') % (range_ac_on, range_ac_off, charging, connected,
                                             charge_left, last_update_date))


if __name__ == '__main__':
    argLen = len(sys.argv)
    if argLen < 2:
        OUT_FILE = 'info.json'
    else:
        OUT_FILE = sys.argv[1]
    get_status(OUT_FILE)
