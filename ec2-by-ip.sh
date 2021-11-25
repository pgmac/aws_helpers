#!/bin/bash

filter=
wildcard=

bork() { echo "Don't do this"
  exit 10
}

while getopts niw opt
do
  case ${opt} in
    n)
      #echo "Searching for instance with a name contain '${OPTARG}'"
      [ -n "${filter}" ] && bork || filter="tag:Name"
    ;;
    i)
      #echo "Searching for instance with an IP address of '${OPTARG}'"
      [ -n "${filter}" ] && bork || filter="network-interface.addresses.private-ip-address"
    ;;
    w)
      wildcard=Y
    ;;
    \?)
      echo "${OPTARG} is an invalid option"
      bork
      exit 2
    ;;
    *)
      echo "Yeah, don't know about this one"
      bork
      exit 3
    ::
  esac
done
shift $((OPTIND-1))

filter=${filter:-"tag:Name"}

if [ -z $1 ]
then
  echo "We need something to search for"
  exit 4
fi

[ -n ${wildcard} ] && searchstr="*${1}*" || searchstr=${1}

echo "Searching ${filter} for ${searchstr}"

aws ec2 describe-instances --output json --filter "Name=${filter}, Values=${searchstr}" --query 'Reservations[*].Instances[*].{Name:Tags[?Key==`Name`]|[0].Value, InstanceId: InstanceId, State: State.Name, IP: NetworkInterfaces[0].PrivateIpAddress, EIP: PublicIpAddress}'

#####
# Reference bits
#####
# By IP
# aws ec2 describe-instances --output json --filter "Name=network-interface.addresses.private-ip-address, Values=${IP}" --query 'Reservations[*].Instances[*].{Name:Tags[?Key==`Name`]|[0].Value,InstanceId:InstanceId,State:State.Name, IP:NetworkInterfaces[0].PrivateIpAddress}'

# By Name
# aws ec2 describe-instances --output table --filter "Name=tag:Name,Values=${IP}" --query 'Reservations[*].Instances[*].{Name:Tags[?Key==`Name`]|[0].Value,InstanceId:InstanceId,State:State.Name, IP:NetworkInterfaces[0].PrivateIpAddress}'
