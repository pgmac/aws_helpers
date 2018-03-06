#!/usr/bin/python3
'''EC2 ssh with filter'''


import sys
from subprocess import call


def get_tag(arr, tagname='Name'):
    '''Just get a single tag'''
    for tag in arr:
        if tag['Key'] == tagname: return tag['Value']


def display_instance(inst):
    '''Display an instances details'''
    #print(inst)
    dispinst = {}
    dispinst['PrivateIpAddress'] = inst['PrivateIpAddress']
    dispinst['KeyName'] = inst['KeyName']
    dispinst['InstanceId'] = inst['InstanceId']
    dispinst['Name'] = get_tag(inst['Tags'], 'Name')
    #dispinst['State'] = inst['State']['Name']
    #print("{:15}\t{}\t{}".format(inst['PrivateIpAddress'], inst['KeyName'], get_tag(inst['Tags'], 'Name')))
    return(dispinst)


def describe_ec2(filter_text):
    '''List AWS EC2 instances'''
    import boto3
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(Filters=[{'Name': 'tag:Name','Values': [filter_text]},{'Name': 'instance-state-name', 'Values': ['running']}])
    results = [display_instance(item) for res in response['Reservations']
                                      for item in res['Instances']]
    ssh_ec2(results)


def ssh_ec2(instances):
    '''Display SSH command for list of instances'''
    _ = [print("ssh {:15}\t{:18}\t{}".format(server['PrivateIpAddress'], server['InstanceId'], server['Name'])) for server in sorted(instances, key=lambda k: k['Name'])]


if __name__ == '__main__':
    results = [describe_ec2(text) for text in sys.argv[1:]]
