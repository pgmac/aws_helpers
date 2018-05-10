#!/usr/bin/python

''' Looks for 3 tags:
SHUTDOWN (boolean)
SHUTDOWN_TIME (HHMM)
STARTUP_TIME (HHMM)

SHUTDOWN tag: true|false
Whether this instance should be shutdown via this script, or not
SHUTDOWN_TIME tag: Hour (24hr) and minute of the day to shutdown
STARTUP_TIME tag:  Hour (24hr) and minute of the day to startup
'''

from boto import ec2
#from os import environ
import datetime

currtime = datetime.datetime.now().time()
thistime = "%02d%02d" % (currtime.hour, currtime.minute)
#thistime = "0605"
#print "It is now: %4s" % (thistime)

conn = ec2.connect_to_region('ap-southeast-2')

for reservation in conn.get_all_instances():
    for instance in reservation.instances:
        #print "%s, %s" % (instance.id, instance.state)
        shutinst = {}
        shutinst["state"] = instance.state
        for tag in instance.tags:
            shutinst[tag] = instance.tags[tag]

        shutinst["state"] = "stopped"
        if "SHUTDOWN" in shutinst:
            if shutinst["SHUTDOWN"] == "true":
                #print "Instance '%s' will shutdown at '%s' and restart at '%s'" % (shutinst["Name"], shutinst["SHUTDOWN_TIME"], shutinst["STARTUP_TIME"])

                if "SHUTDOWN_TIME" in shutinst:
                    if shutinst["SHUTDOWN_TIME"] <= thistime and shutinst["state"] == "running":
                        print("Shutting down: {:10s} '{}' ".format(instance.id, shutinst["Name"]))
                        #conn.stop_instances(instance_ids=[instance.id])

                if "STARTUP_TIME" in shutinst:
                    if shutinst["STARTUP_TIME"] <= thistime and shutinst["state"] == "stopped":
                        print("Starting up: {:10s} '{}'".format(instance.id, shutinst["Name"]))
                        #conn.start_instances(instance_ids=[instance.id])
                        for upres in conn.get_all_instances(instance_ids=instance.id):
                            for upinst in upres.instances:
                                #print upinst
                                print("Using IP {}".format(upinst.ip_address))

            #if shutinst["SHUTDOWN"] == "someothervalue":
            #   Do other tasks. EG: force/ensure shutdown, force/ensure startup, terminate
        #print "==================="
