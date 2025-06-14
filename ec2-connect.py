#!/usr/bin/env -S uv run --script
"""Filter your list of EC2s to connect to, either via SSH or SSM
You need to install the SSM session manager: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html
"""


# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "appkit>=0.2.8",
#     "boto3>=1.38.33",
#     "botocore>=1.38.33",
#     "iterm2>=2.10",
#     "jmespath>=1.0.1",
#     "python-dateutil>=2.9.0.post0",
#     "s3transfer>=0.13.0",
#     "simple-term-menu>=1.6.6",
#     "six>=1.17.0",
#     "urllib3>=2.4.0",
# ]
# ///

from argparse import ArgumentParser
from os import system as sysexec
from os.path import exists
from platform import system

from simple_term_menu import TerminalMenu


def get_tag(arr, tagname="Name"):
    """Just get a single tag"""
    for tag in arr:
        if tag["Key"] == tagname:
            return tag["Value"]


def check_key(args):
    """Verify a specified key exists on the filesystem"""
    if exists(args.key):
        return


def display_instance(inst):
    """Display an instances details"""
    dispinst = {}
    dispinst["PrivateIpAddress"] = inst["PrivateIpAddress"]
    dispinst["PublicIpAddress"] = inst.get("PublicIpAddress", "127.0.0.1")
    dispinst["KeyName"] = inst.get("KeyName", "id_rsa")
    dispinst["InstanceId"] = inst["InstanceId"]
    dispinst["Name"] = get_tag(inst["Tags"], "Name")
    return dispinst


def case_insensivise(case_str):
    """Return common character case variants for a string"""

    str_arr = []
    str_arr.append("*{}*".format(case_str))
    str_arr.append("*{}*".format(case_str.lower()))
    str_arr.append("*{}*".format(case_str.capitalize()))
    str_arr.append("*{}*".format(case_str.upper()))

    return str_arr


def describe_ec2(filter_args):
    """List AWS EC2 instances"""
    import boto3

    if filter_args.search == "Name":
        _filter_name = "tag:Name"
    elif filter_args.search == "PublicIp":
        _filter_name = "network-interface.addresses.public-ip-address"
    elif filter_args.search == "PrivateIp":
        _filter_name = "network-interface.addresses.private-ip-address"
    elif filter_args.search == "InstanceId":
        _filter_name = "instance-id"

    ec2 = boto3.client("ec2")
    for text in filter_args.text:
        # print(f"Searching for EC2 instances matching '*{text}*'")
        response = ec2.describe_instances(
            Filters=[
                {"Name": _filter_name, "Values": case_insensivise(text)},
                {"Name": "instance-state-name", "Values": ["running"]},
            ]
        )
        results = [
            display_instance(item)
            for res in response["Reservations"]
            for item in res["Instances"]
        ]
        results = sorted(results, key=lambda k: (k["Name"], k["InstanceId"]))
        if filter_args.all and not filter_args.ssh and not filter_args.ssm:
            list_ec2(results)
        else:
            if len(results) > 0:
                results = select_ec2(results)

        return results


def connect_instance_ssh(results, filter_args):
    """Connect to AWS EC2 instance(s)"""

    if len(results) > 0:
        # print("Taking you to {} ({})".format(results['Name'], results['InstanceId']))
        ssh_ec2(results, filter_args)
    else:
        print("No instances found to connect to")


def connect_instance_ssm(results, filter_args):
    """Connect to AWS EC2 instance(s)"""

    if len(results) > 0:
        # print("Taking you to {} ({})".format(results['Name'], results['InstanceId']))
        ssm_ec2(results, filter_args)
    else:
        print("No instances found to connect to")


def select_ec2(instances):
    """Allow you to select a single instance from all of the instances returned to connect to"""
    options = [
        ("{}:{}".format(instance["InstanceId"], instance["Name"]))
        for instance in instances
    ]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    try:
        return [instances[menu_entry_index]]
    except:
        return []


def list_ec2(instances):
    """Display the list of instances to connect to"""
    print("Found {} instances you can connect to".format(len(instances)))
    _ = [
        print("Connecting to {:18}\t{}".format(server["InstanceId"], server["Name"]))
        for server in instances
    ]


async def iterm_ssh(connection):
    """Open a new window to make the connection in"""
    """This currently doesn't work (as you can see via the command below)"""
    import iterm2

    app = await iterm2.async_get_app(connection)
    await app.async_activate()
    await iterm2.Window.async_create(connection, command="/bin/bash -l -c vi")


def ssh_ec2(instances, fargs):
    """Connect to instances via SSH command"""

    # Clean up and decorate some options
    fargs.username = fargs.username + "@" if fargs.username else ""
    fargs.cipher = " -c " + fargs.cipher if fargs.cipher else ""

    if fargs.window:
        if system() == "Darwin":
            import iterm2
            from AppKit import NSWorkspace

            NSWorkspace.sharedWorkspace().launchApplication_("iTerm2")
            iterm2.run_until_complete(iterm_ssh, True)
        elif system() == "Linux":
            _ = [
                sysexec(
                    f"ssh {fargs.username}{server['{}Address'.format(fargs.remote)]}{fargs.cipher}"
                )
                for server in instances
            ]
        else:
            print("Don't know how to terminal on this system")
            exit(10)
    else:
        _ = [
            sysexec(
                f"ssh {fargs.username}{server['{}Address'.format(fargs.remote)]}{fargs.cipher}"
            )
            for server in instances
        ]


def ssm_ec2(instances, fargs):
    """Connect to the EC2 instance(s) via an SSM Session"""

    if fargs.window:
        # Open a new terminal window - it doesn't do it yet, but it will do .... someday
        try:
            if system() == "Darwin":
                import iterm2
                from AppKit import NSWorkspace

                NSWorkspace.sharedWorkspace().launchApplication_("iTerm2")
                iterm2.run_until_complete(iterm_ssh, True)
            elif system() == "Linux":
                _ = [
                    sysexec(
                        f"gnome-terminal -e 'aws ssm start-session --target {server['InstanceId']}'"
                    )
                    for server in instances
                ]
            else:
                print("Don't know how to terminal on this system")
                exit(10)
        except Exception as e:
            print("Error opening new terminal window: {}".format(e))
            exit(1)
    else:
        # Connect to the instance(s) via SSM
        try:
            _ = [
                sysexec(f"aws ssm start-session --target {server['InstanceId']}")
                for server in instances
            ]
        except Exception as e:
            print("Error connecting to instance(s) via SSM: {}".format(e))
            exit(1)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "text", help="String to search for in the NAME tag of EC2 instances", nargs=1
    )
    parser.add_argument(
        "--all",
        help="When True: Connect to all EC2 instances searched for. When False: Interactively select which instance to connect to. Default: False",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--window",
        help="Open the connection in a new window",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--search",
        choices=["Name", "PrivateIp", "PublicIp", "InstanceId"],
        nargs="?",
        default="Name",
        help="Search for your EC2 instane(s) on this",
    )
    # parser.set_defaults(func=describe_ec2)
    connections = parser.add_subparsers(
        title="Connection Type",
        description="Choose a connection type",
        dest="connection",
        required=True,
        help="Choose how you want to connect to the instance(s)",
    )
    ssh_connection = connections.add_parser(
        "ssh", help="Connection via SSH to the EC2 instance(s)"
    )
    ssh_connection.add_argument(
        "--remote",
        choices=["PrivateIp", "PublicIp"],
        default="PrivateIp",
        help="Connect to the EC2 instance(s) on this",
    )
    ssh_connection.add_argument(
        "-i",
        "--identity",
        type=str,
        help="SSH key to use to identify yourself to the EC2 instance(s)",
    )
    ssh_connection.add_argument(
        "--username", type=str, help="The username to connect to the instance(s) as"
    )
    # ssh_connection.add_argument('--sshkey', '--key', type=str, help="The ssh key to connect to the instance(s)", nargs='?')
    ssh_connection.add_argument(
        "-c",
        "--cipher",
        type=str,
        help="The cipher to use to secure connections to the instance(s)",
        default="",
        nargs="?",
    )

    ssm_connection = connections.add_parser(
        "ssm", help="Connection to the instance(s) via the AWS SSM agent"
    )
    # ssm_connection.set_defaults(func=connect_instance_ssm)

    args = parser.parse_args()
    ec2s = describe_ec2(args)
    if args.connection == "ssh":
        connect_instance_ssh(ec2s, args)
    elif args.connection == "ssm":
        connect_instance_ssm(ec2s, args)


if __name__ == "__main__":
    main()
