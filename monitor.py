#!/usr/bin/env python3

import os
import sys
import subprocess

TIMEOUT = 10

capture_cmd_fmt = "tcpdump -l -s 64 -e -p -Ini {} type mgt subtype probe-req"

if __name__ == "__main__":

    IFACE = "en0"

    # must be running as root
    if os.geteuid() != 0:
        print("Requires privileges to capture on {}. Elevating to root...".format(IFACE))
        os.execvp("sudo", ["sudo"] + sys.argv) # replace process

    try:
        while True:
            mac_hash = {}
            try:
                subprocess.run(capture_cmd_fmt.format(IFACE).split(), timeout=TIMEOUT, stdout=subprocess.PIPE, encoding="utf-8")
                # here goes error handling - tcpdump should just run until killed
            except subprocess.TimeoutExpired as e:
                dump = e.stdout.split("\n")
                print("{} lines received".format(len(dump)))

                for line in dump:
                    # relevant fields by index
                    # timestamp: 0, signal strength: 10, SA: 18
                    frame = line.split()
                    if len(frame) == 31: # this is a good frame
                        tstamp = frame[0]
                        ss = frame[10] # -XXdBm
                        sa_mac = frame[18]
                        mac_hash[sa_mac] = 1

            print("{} unique devices detected".format(len(mac_hash.keys())))
            input()
    except KeyboardInterrupt:
        print("Done.")

