# Litmus: monitor
Analyses IEEE802.11 probe request frames to approximate attendance

## Running monitor on macOS

1. Use the Airport CLI, found at `/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport`
2. Dissociate interface from any AP with `airport -z`
3. Capture link-level 802.11 frames with `airport en0 sniff` (where `en0` is most likely your wireless interface - check with `ifconfig`)
4. Analyse captured binary frames for Probe Request packets using `tcpdump -s 24 -e -r /tmp/airportSniffxxxxx.cap type mgt subtype probe-req`

## Running monitor on Linux

It's important to first confirm both the physical device layer and driver support monitor mode (specifically capturing management probe request frames).
Something like `iw list` should do it.

1. Create a new wireless interface in monitor mode and delete the managed mode interface
2. Bring the new monitor interface up and select a channel (or cycle through channels)
3. Run tcpdump to capture Probe Request Management frames

## Putting this together

Once we've established which OS the monitor is to be deployed on, it's a matter of having a Python script run a
data frame capture in monitor mode for some interval of time, parse the results of `tcpdump`, set the interface back up
to managed mode on an AP, and push a data update to the Litmus API server.

## Sources:

[Linux kernel iw documentation](https://wireless.wiki.kernel.org/en/users/documentation/iw#listening_to_events)
[802.11 Network Structures](https://sarwiki.informatik.hu-berlin.de/802.11_Network_Structures#Probe_Request_Frame)
[Wireshark: Monitor mode on OS X](https://wiki.wireshark.org/CaptureSetup/WLAN#Mac_OS_X)

A related project: [schollz/find-lf](https://github.com/schollz/find-lf)

