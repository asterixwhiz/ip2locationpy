#!/usr/bin/env python3
# # Copyright (C) 2005-2016 IP2Location.com
# All Rights Reserved
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the MIT license

import csv
import os
import os.path
import sys
import import_declare_test
import IP2Location
import IP2Proxy

module_dir = os.path.dirname(os.path.realpath(__file__))
app_dir = os.path.abspath(os.path.join(module_dir, os.pardir))
data_path = os.path.join(app_dir, "data")


def main():

    ipfield = sys.argv[1]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)
    r.fieldnames

    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    ip2locationdatabase = IP2Location.IP2Location()
    ip2proxydatabase = IP2Proxy.IP2Proxy()

    ip2locationgeofile = os.path.join(data_path, "ip2locationgeodb.bin")
    ip2locationproxyfile = os.path.join(data_path, "ip2locationproxydb.bin")

    if os.path.isfile(ip2locationgeofile):
        ip2locationdatabase.open(ip2locationgeofile)
        ip2locationlookupfileavaliable=1
    else:
        ip2locationlookupfileavaliable=0
    if os.path.isfile(ip2locationproxyfile):
        ip2proxydatabase.open(ip2locationproxyfile)
        ip2proxylookupfileavaliable=1
    else:
        ip2proxylookupfileavaliable=0
    for result in r:
        #try:
        if ip2proxylookupfileavaliable == 1:
            #print(f'ipfield:{result[ipfield]}')
            ip2proxyresponse = ip2proxydatabase.get_all(result[ipfield])
            result["is_proxy"] = ip2proxyresponse['is_proxy']
            result["proxy_type"] = ip2proxyresponse['proxy_type']
            result["country_short"] = ip2proxyresponse['country_short']
            result["country_long"] = ip2proxyresponse['country_long']
            result["region"] = ip2proxyresponse['region']
            result["city"] = ip2proxyresponse['city']
            result["isp"] = ip2proxyresponse['isp']
            result["domain"] = ip2proxyresponse['domain']
            result["usage_type"] = ip2proxyresponse['usage_type']
            result["asn"] = ip2proxyresponse['asn']
            result["as_name"] = ip2proxyresponse['as_name']
            result["last_seen"] = ip2proxyresponse['last_seen']
            result["threat"] = ip2proxyresponse['threat']
            result["provider"] = ip2proxyresponse['provider']
        if ip2locationlookupfileavaliable == 1:
            #print(f'ipfield:{result[ipfield]}')
            ip2locationresponse = ip2locationdatabase.get_all(result[ipfield])
            result["country_short"] = ip2locationresponse.country_short
            result["country_long"] = ip2locationresponse.country_long
            result["region"] = ip2locationresponse.region
            result["city"] = ip2locationresponse.city
            result["isp"] = ip2locationresponse.isp
            result["latitude"] = ip2locationresponse.latitude
            result["longitude"] = ip2locationresponse.longitude
            result["domain"] = ip2locationresponse.domain
            result["zipcode"] = ip2locationresponse.zipcode
            result["timezone"] = ip2locationresponse.timezone
            result["netspeed"] = ip2locationresponse.netspeed
            result["idd_code"] = ip2locationresponse.idd_code
            result["area_code"] = ip2locationresponse.area_code
            result["weather_code"] = ip2locationresponse.weather_code
            result["weather_name"] = ip2locationresponse.weather_name
            result["mobile_brand"] = ip2locationresponse.mobile_brand
            result["elevation"] = ip2locationresponse.elevation
            result["usage_type"] = ip2locationresponse.usage_type
            result["address_type"] = ip2locationresponse.address_type
            result["category"] = ip2locationresponse.category
        w.writerow(result)
    ip2locationdatabase.close()
    ip2proxydatabase.close()
main()
