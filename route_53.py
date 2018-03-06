#!/usr/bin/python3
"""List the Route 53 DNS Entries"""

from pprint import pprint
import boto3
from botocore.exceptions import ClientError

def rr_display(client, rrset, level=0):
    #print(rrset)
    print("{}{}\t{}".format("\t"*level, rrset['Name'], rrset['Type']))
    print("{}{}".format("\t"*(level+1), rrset['ResourceRecords']))

def zone_display(client, zone_det, level=0):
    """Display the zone details"""
    print("{}{}".format("\t"*level, zone_det['Name']))
    #print(zone_det)
    response = client.list_resource_record_sets(HostedZoneId=zone_det['Id'])
    zone = [rr_display(client, rrset, (level+1)) for rrset in response['ResourceRecordSets']]
    return zone

def main():
    """Get the details"""
    r53 = boto3.client('route53')
    try:
        response = r53.list_hosted_zones()
        zones = [zone_display(r53, item) for item in response['HostedZones']]
        #pprint(out_put)
        #_ = (print(out_item) for out_item in out_put)
    except ClientError as c_e:
        print(c_e)

    return zones

if __name__ == '__main__':
    main()
