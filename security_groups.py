#!/usr/bin/python3
"""List the security groups"""
import boto3
import sys
from botocore.exceptions import ClientError

def main(filter_text="*"):
    """Do the main things"""
    ec2 = boto3.client('ec2')

    try:
        response = ec2.describe_security_groups(Filters=[{'Name': 'tag:Name','Values': [filter_text]}])
        if len(response['SecurityGroups']) == 0 and filter_text[:3] == 'sg-':
        	response = ec2.describe_security_groups(GroupIds=[filter_text])
	
        #pprint(response['SecurityGroups'])
        for group in sorted(response['SecurityGroups'], key=lambda k: k['Description']):
            print("{}: {}".format(group['GroupId'], group['Description']))
            for rule in group['IpPermissions']:
                for iprange in sorted(rule['IpRanges'], key=lambda l: l['CidrIp']):
                    rule['IpProtocol'] = 'any' if rule['IpProtocol'] == "-1" else rule['IpProtocol']
                    print("\tAllow {} {}-{} from {}".format(rule['IpProtocol'], rule.get('FromPort', 'all'), rule.get('ToPort', 'all'), iprange['CidrIp']))
                for sg in sorted(rule.get('UserIdGroupPairs', []), key=lambda m: m['GroupId']):
                    print("\tAllow {}".format(sg['GroupId']))
                    #main(sg['GroupId'])

    except ClientError as c_e:
        print(c_e)

if __name__ == '__main__':
    _= [main(text) for text in sys.argv[1:]]
