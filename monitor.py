#!/usr/bin/env python3

import os
import sys
import subprocess
import time

TMPDIR = os.path.dirname("tmp/")

# Reference: https://en.wikipedia.org/wiki/List_of_WLAN_channels
# Let's only focus on a subset (18) of channels allowed in the US
IEEE80211_CHANNELS_5G = [36,38,40,42,44,46,48]

IEEE80211_CHANNELS = [1,2,3,4,5,6,7,8,9,10,11,36,38,40,42,44,46,48]
#IEEE80211_CHANNELS = IEEE80211_CHANNELS_5G

TIMEOUT = 30
HOP_INTERVAL = 1.7

capture_cmd_fmt = "tcpdump -U -s 64 -e -p -Ini {} type mgt subtype probe-req -w {}"
decode_cmd_fmt = "tcpdump -r {} -e"
link_down_cmd = "airport -z" # NOTE: platform dependent (macOS)
channel_cmd_fmt = "airport --channel={}" # NOTE: platform dependent (macOS)
info_cmd = "airport -I" # NOTE: platform dependent (macOS)
connect_cmd_fmt = "networksetup -setairportnetwork {} {}" # NOTE: platform dependent (macOS)

SA_FIELD = "SA:"

def get_ssid():
    res = subprocess.run(info_cmd.split(), stdout=subprocess.PIPE, encoding="utf-8")
    for line in res.stdout.split("\n"):
        k,v = line.lstrip().split(" ", 1) # split on first occurrence
        if k == "SSID:":
            return v

def reconnect_ap(interface, ssid):
    subprocess.run(connect_cmd_fmt.format(interface,ssid).split()) # connect back to the AP (assume no PSK...)

def capture_channel(interface, chan):
    subprocess.run(channel_cmd_fmt.format(chan).split()) # switch channel
    # error handling? platform checks? fuck it

    fileout = os.path.join(TMPDIR,"channel_{}.cap".format(chan))
    child = subprocess.Popen(capture_cmd_fmt.format(interface,fileout).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    start = time.time()
    # wait HOP_INTERVAL seconds for tcpdump to capture any frames on this channel
    while time.time() - start < HOP_INTERVAL:
        pass

    child.terminate()
    child.wait()

    child = subprocess.Popen(decode_cmd_fmt.format(fileout).split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding="utf-8")
    stdout, _ = child.communicate()

    dump = stdout.split("\n")

    mac_hash = {} # unique MAC addresses (maybe map to something useful?)
    for line in dump:
        # relevant fields by index
        # timestamp: 0, signal strength: 10, SA: 18
        frame = line.split()
        sa_mac = ""
        for f in frame:
            if f.startswith(SA_FIELD):
                sa_mac = f[len(SA_FIELD):]

        if sa_mac:
            mac_hash[sa_mac] = 1

    return mac_hash

if __name__ == "__main__":

    IFACE = "en0"

    # must be running as root
    if os.geteuid() != 0:
        print("Requires privileges to capture on {}. Elevating to root...".format(IFACE))
        os.execvp("sudo", ["sudo"] + sys.argv) # replace process

    ssid = get_ssid()
    print("SSID: {}".format(ssid))

    if not os.path.exists(TMPDIR):
        os.mkdir(TMPDIR)

    try:
        while True:
            subprocess.run(link_down_cmd.split()) # bring the link down for monitor mode

            t = time.time()
            all_macs = {}
            for i,channel in enumerate(IEEE80211_CHANNELS):
                if time.time() - t > TIMEOUT:
                    break

                mac_hash = capture_channel(IFACE, channel)
                for k in mac_hash.keys():
                    all_macs[k] = 1

                sys.stdout.write(".")
                sys.stdout.flush()

            sys.stdout.write("\n")

            print("{} WiFi devices detected".format(len(all_macs.keys()), channel))

            reconnect_ap(IFACE, ssid)
            subprocess.run(["curl", "www.example.com"])
            input()

    except KeyboardInterrupt:
        if not get_ssid():
            print("Restoring AP...")
            reconnect_ap(IFACE, ssid)

        print("Done.")

    # cleanup:
    for f in os.listdir(TMPDIR):
        os.remove(os.path.join(TMPDIR,f))
    os.rmdir(TMPDIR)

