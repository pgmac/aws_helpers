#!/usr/bin/python3

import argparse

parser = argparse.ArgumentParser()
#parser.add_argument("echo", help="echo the string you use here")
parser.add_argument("square", help="Display the square of the given number", type=int, default=1)
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="count", default=0)
args = parser.parse_args()
#print(args.echo)

if args.verbose >= 2:
    print("Verbosity turned on")
    print("{} squared equals {}".format(args.square, args.square**2))
elif args.verbose >= 1:
    print("Verbosity turned on")
    print("{}^2={}".format(args.square, args.square**2))
else:
    print(args.square**2)