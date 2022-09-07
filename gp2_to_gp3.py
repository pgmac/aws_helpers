#!/usr/bin/python3
'''
This started out life as a practical example of setting up an AWS SSM Automation task, but this doesn't do that anymore.
Convert all GP2 volumes to GP3 volumes
'''

import boto3
from botocore.exceptions import ClientError


def tags_to_dict(resource):
    '''Convert the Tags structure into a python dict - because I'm lazy'''

    ObjTags = {}
    try:
        for tag_key in resource['Tags']:
            ObjTags[tag_key['Key']] = tag_key['Value']
    except:
        pass
    
    return ObjTags


def get_gp2_volumes():
    '''Get a list of all of the GP2 volumes'''

    client = boto3.client('ec2')
    response = client.describe_volumes(
    Filters=[
        {
            'Name': 'volume-type',
            'Values': [
                'gp2',
            ]
        },
    ])

    return response


def gp2_to_gp3(volumes):
    '''Convert the list of GP2 volumes to GP3'''

    results = []

    client = boto3.client('ec2')
    for volume in volumes['Volumes']:
        try:
            response = client.modify_volume(
                DryRun=True,
                VolumeId=volume['VolumeId'],
                VolumeType='gp3')
            results['succeeded'].append("{} {}".format(volume['VolumeId'], tags_to_dict(volume['Tags']).get('Name', volume['VolumeId'])))
        except BaseException as e:
            results['failed'].append("{} {}: {}".format(volume['VolumeId'], tags_to_dict(volume['Tags']).get('Name', volume['VolumeId']), e.message))
            continue

    return results


def display_results(results):
    '''Show me how the converions went'''
    for status in results:
        print("Volume conversions {}".status)
        for volume in status:
            print(volume)


def main():
    volumes = get_gp2_volumes()
    conv_results = gp2_to_gp3(volumes)
    display_results(conv_results)


if __name__ == '__main__':
    main()