#!/usr/bin/python3
'''Get tag details for all AWS resources'''


import sys
#from subprocess import call


def get_tag(arr, tagname='Name'):
    '''Just get a single tag'''
    for tag in arr:
        if tag['Key'] == tagname: return tag['Value']


def object_details(inst, idkey="InstanceId"):
    '''Display an instances details'''
    dispinst = {}
    dispinst[idkey] = inst[idkey]
    dispinst['Name'] = get_tag(inst['Tags'], 'Name')
    req_tags = [
        'Ansible',
        'CS-ENV',
        'CS-REGION',
        'CS-AZ',
        'CS-PRODUCT',
        'CS-APP',
        'CS-VERSION',
        'CS-RESOURCETYPE',
        'CS-DEVELOPER',
        'CS-STORYID',
        'CS-TEMPORARY',
        'CS-EXPIRYDATE',
        'Inventory',
        'Role',
        'CS-UTILITY-POWER',
        'CS-UTILITY-POWER-ON',
        'CS-UTILITY-POWER-OFF',
        'CS-UTILITY-REPOSITORY'
    ]
    for tag in req_tags:
        dispinst[tag] = get_tag(inst['Tags'], tag)

    return(dispinst)


def describe_ec2(filter_text):
    '''List AWS EC2 instances'''
    import boto3
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(Filters=[
        {'Name': 'tag:Name', 'Values': [filter_text]}
    ]) 
    results = [object_details(item) for res in response['Reservations']
                                      for item in res['Instances']]
    csv_out(results, 'ec2.csv')

    response = ec2.describe_volumes(Filters=[
        {'Name': 'tag:Name', 'Values': [filter_text]}
    ])
    results = [object_details(vol, "VolumeId") for vol in response['Volumes']]
    csv_out(results, 'vol.csv')

    response = ec2.describe_snapshots(Filters=[
        {'Name': 'tag:Name', 'Values': [filter_text]}
    ])
    results = [object_details(snap, "SnapshotId") for snap in response['Snapshots']]
    csv_out(results, 'snap.csv')

    response = ec2.describe_vpcs(Filters=[
        {'Name': 'tag:Name', 'Values': [filter_text]}
    ])
    results = [object_details(vpc, "VpcId") for vpc in response['Vpcs']]
    csv_out(results, 'vpc.csv')

    response = ec2.describe_images(Filters=[
        {'Name': 'tag:Name', 'Values': [filter_text]}
    ])
    #print(response)
    results = [object_details(image, "ImageId") for image in response['Images']]
    #print(results)
    csv_out(results, 'images.csv')


def describe_lbs(filter_text):
    '''List AWS load balancers'''
    import boto3
    lb = boto3.client('elb')
    response = lb.describe_load_balancers()
    print(response)
    results = [object_details(lb.describe_tags(LoadBalancerNames=[onelb['LoadBalancerName']])['TagDescriptions'], "LoadBalancerName") for onelb in response['LoadBalancerDescriptions']]
    csv_out(results, 'lbs.csv')


def describe_aws(filter_text):
    describe_ec2(filter_text)
    describe_lbs(filter_text)


def csv_out(instances, csv_file="data.csv"):
    '''Display SSH command for list of instances'''
    import csv
    import os
    #_ = [print("{:18},{}".format(server['InstanceId'], server['Name'])) for server in sorted(instances, key=lambda k: k['Name'])]
    #print(instances)
    aws_env = os.environ.get('AWS_PROFILE', 'DEV')
    csv_file = ("{}-{}".format(aws_env, csv_file))

    try:
        with open(csv_file, 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(instances[0].keys())
            _ = [wr.writerow(instance.values()) for instance in sorted(instances, key=lambda k: k['Name'])]
    except:
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.argv.append('*')
    _ = [describe_aws(text) for text in sys.argv[1:]]
    #results = [describe_ec2(text) for text in sys.argv[1:]]
