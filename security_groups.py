#!/usr/bin/python3
"""List the security groups"""
import boto3
from botocore.exceptions import ClientError

def main():
    """Do the main things"""
    ec2 = boto3.client('ec2')

    try:
        response = ec2.describe_security_groups()
        #pprint(response['SecurityGroups'])
        for group in sorted(response['SecurityGroups'], key=lambda k: k['Description']):
            print("{}: {}".format(group['GroupId'], group['Description']))
            for rule in group['IpPermissions']:
                for iprange in sorted(rule['IpRanges'], key=lambda l: l['CidrIp']):
                    rule['IpProtocol'] = 'any' if rule['IpProtocol'] == "-1" else rule['IpProtocol']
                    print("\tAllow {} {}-{} from {}".format(rule['IpProtocol'], rule.get('FromPort', 'all'), rule.get('ToPort', 'all'), iprange['CidrIp']))
                for sg in sorted(rule.get('UserIdGroupPairs', []), key=lambda m: m['GroupId']):
                    print("\tAllow {}".format(sg['GroupId']))

    except ClientError as c_e:
        print(c_e)

if __name__ == '__main__':
    main()
