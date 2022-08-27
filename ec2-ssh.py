#!/usr/bin/env python3
'''Filter your list of EC2s to connect to, either via SSH or SSM'''


from sys import argv
from platform import system
from os import environ
from os import system as sysexec
from platform import system
from argparse import ArgumentParser
from subprocess import Popen
from AppKit import NSWorkspace
import iterm2
from simple_term_menu import TerminalMenu


def get_tag(arr, tagname='Name'):
    '''Just get a single tag'''
    for tag in arr:
        if tag['Key'] == tagname:
            return tag['Value']


def display_instance(inst):
    '''Display an instances details'''
    dispinst = {}
    dispinst['PrivateIpAddress'] = inst['PrivateIpAddress']
    dispinst['KeyName'] = inst.get('KeyName', 'ansible_ec2_key')
    dispinst['InstanceId'] = inst['InstanceId']
    dispinst['Name'] = get_tag(inst['Tags'], 'Name')
    return(dispinst)


def describe_ec2(filter_args):
    '''List AWS EC2 instances'''
    import boto3

    _filter_name = 'tag:Name'
    if filter_args.privateip:
        _filter_name = 'network-interface.addresses.private-ip-address'
    if filter_args.instanceid:
        _filter_name = 'instance-id'

    ec2 = boto3.client('ec2')
    for text in filter_args.text:
        #print(f"Searching for EC2 instances matching '*{text}*'")
        response = ec2.describe_instances(Filters=[{'Name': _filter_name, 'Values': ["*{}*".format(text)]}, {'Name': 'instance-state-name', 'Values': ['running']}])
        results = [display_instance(item) for res in response['Reservations']
                   for item in res['Instances']]
        results = sorted(results, key=lambda k: (k['Name'], k['InstanceId']))
        if filter_args.all and not filter_args.ssh and not filter_args.ssm:
            list_ec2(results)
        else:
            if len(results) > 1: results = select_ec2(results)

        if len(results) > 0 :
            #print("Taking you to {} ({})".format(results['Name'], results['InstanceId']))
            if filter_args.ssh:
                ssh_ec2(results, filter_args)
            if filter_args.ssm:
                ssm_ec2(results, filter_args)
        else:
            print("No instances found to connect to")


def select_ec2(instances):
    '''Allow you to select a single instance from all of the instances returned to connect to'''
    options = [("{}:{}".format(instance['InstanceId'], instance['Name'])) for instance in instances]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    try:
       #return [{"InstanceId": options[menu_entry_index].split(':')[0], "Name": options[menu_entry_index].split(':')[1]}]
       return [instances[menu_entry_index]]
    except:
       return []


def list_ec2(instances):
    '''Display the list of instances to connect to'''
    print("Found {} instances you can connect to".format(len(instances)))
    _ = [print("Connecting to {:18}\t{}".format(server['InstanceId'], server['Name'])) for server in instances]


async def iterm_ssh(connection):
    '''Open a new window to make the connection in'''
    '''This currently doesn't work (as you can see via the command below)'''
    app = await iterm2.async_get_app(connection)
    await app.async_activate()
    await iterm2.Window.async_create(connection, command="/bin/bash -l -c vi")


def ssh_ec2(instances, fargs):
    '''Connect to instances via SSH command'''

    if fargs.user:
        fargs.user = fargs.user+"@"
    else:
        fargs.user = ""
    if fargs.window:
        if system() == "Darwin":
            NSWorkspace.sharedWorkspace().launchApplication_("iTerm2")
            iterm2.run_until_complete(iterm_ssh, True)
        elif system() == "Linux":
            _ = [sysexec("{}ssh {}".format(fargs.user, server['PrivateIpAddress'])) for server in instances]
        else:
            print("Don't know how to terminal on this system")
            exit(10)
    else:
        _ = [sysexec("{}ssh {}".format(fargs.user, server['PrivateIpAddress'])) for server in instances]


def ssm_ec2(instances, fargs):
    '''Connect to the EC2 instance(s) via an SSM Session'''

    if fargs.window:
        # Open a new terminal window
        _ = [sysexec("aws ssm start-session --target {}".format(server['InstanceId'])) for server in instances]
    else:
        _ = [sysexec("aws ssm start-session --target {}".format(server['InstanceId'])) for server in instances]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("text", help="String to search for in the NAME tag of EC2 instances", nargs="+")
    parser.add_argument("--all", help="When True: Connect to all EC2 instances searched for. When False: Interactively select which instance to connect to. Default: False", action="store_true", default=False)
    instance = parser.add_mutually_exclusive_group()
    instance.add_argument("-i", "--instanceid", help="Search for EC2 instance(s) using the Instance ID", action="store_true")
    instance.add_argument("-p", "--privateip", help="Search for EC2 instance(s) using the IP address", action="store_true")
    connection = parser.add_mutually_exclusive_group()
    connection.add_argument("--ssm", help="Connect via a SSM Session to the EC2 instance(s)", action="store_true", default=False)
    connection.add_argument("--ssh", help="Connect via SSH to the EC2 instance(s)", action="store_true", default=False)
    parser.add_argument("-u", "--user", help="User to connect as (SSH only)")
    parser.add_argument("-w", "--window", help="Open the connection in a new window", action="store_true", default=False)
    parser.add_argument("-c", "--case-sensitive", help="Perform a case-sensitive seearch", action="store_true", default=False)
    args = parser.parse_args()
    describe_ec2(args)
