#!/usr/bin/env python3
'''EC2 ssh with filter'''


from sys import argv
from platform import system
from os import environ
from os import system as sysexec
from argparse import ArgumentParser
from subprocess import Popen


def get_tag(arr, tagname='Name'):
    '''Just get a single tag'''
    for tag in arr:
        if tag['Key'] == tagname: return tag['Value']


def display_instance(inst):
    '''Display an instances details'''
    #print(inst)
    dispinst = {}
    dispinst['PrivateIpAddress'] = inst['PrivateIpAddress']
    dispinst['KeyName'] = inst.get('KeyName', 'ansible_ec2_key')
    dispinst['InstanceId'] = inst['InstanceId']
    dispinst['Name'] = get_tag(inst['Tags'], 'Name')
    #dispinst['State'] = inst['State']['Name']
    #print("{:15}\t{}\t{}".format(inst['PrivateIpAddress'], inst['KeyName'], get_tag(inst['Tags'], 'Name')))
    return(dispinst)


def describe_ec2(filter_args):
    '''List AWS EC2 instances'''
    import boto3

    _filter_name = 'tag:Name'
    if filter_args.privateip: _filter_name = 'network-interface.addresses.private-ip-address'
    if filter_args.instanceid: _filter_name = 'instance-id'

    ec2 = boto3.client('ec2')
    for text in filter_args.text:
        response = ec2.describe_instances(Filters=[{'Name': _filter_name, 'Values': [text]}, {'Name': 'instance-state-name', 'Values': ['running']}])
        results = [display_instance(item) for res in response['Reservations']
                                          for item in res['Instances']]
        ssh_ec2(results, filter_args)


def ssh_ec2(instances, fargs):
    '''Display SSH command for list of instances'''

    terminal_clients = {
        'Darwin': 'iterm',
        'Linux':  ['x-terminal-emulater', '-e'],
    }

    _ = [print("ssh {:15}\t{:18}\t{}".format(server['PrivateIpAddress'], server['InstanceId'], server['Name'])) for server in sorted(instances, key=lambda k: k['Name'])]
    if fargs.connect:
        if fargs.user:
            #_ = [Popen([terminal_clients[system()], "ssh", "{}@{}".format(fargs.user, server['PrivateIpAddress'])]) for server in sorted(instances, key=lambda k: k['Name'])]
            _ = [sysexec("ssh {}@{}".format(fargs.user, server['PrivateIpAddress'])) for server in sorted(instances, key=lambda k: k['Name'])]
        else:
            #_ = [Popen([terminal_clients[system()], "ssh", "{}".format(server['PrivateIpAddress'])]) for server in sorted(instances, key=lambda k: k['Name'])]
            _ = [sysexec("ssh {}".format(server['PrivateIpAddress'])) for server in sorted(instances, key=lambda k: k['Name'])]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("text", help="String to search for in the NAME tag of EC2 instances", nargs="+")
    parser.add_argument("-i", "--instanceid", help="Search for EC2 instance(s) using the Instance ID", action="store_true")
    parser.add_argument("-p", "--privateip", help="Search for EC2 instance(s) using the IP address", action="store_true")
    parser.add_argument("-c", "--connect", help="Connect via SSH to the EC2 instance(s)", action="store_true")
    parser.add_argument("-u", "--user", help="User to connect as")
    args = parser.parse_args()
    #results = [describe_ec2(text) for text in argv[1:]]
    describe_ec2(args)
