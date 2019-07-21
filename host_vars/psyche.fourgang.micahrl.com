---
# ifcfg:

#   # TODO: how do you get hwaddr in advance?
#   hwaddr: B8:27:EB:73:D2:86

#   # Optional value - maybe don't use this?
#   # This is system specific and can be created using ‘uuidgen eth0’ command
#   uuid: 472874fb-810d-3e6b-9225-3af44158275d

#   address6: "{{ cluster_ipv6net | ipaddr(10) | ipaddr('host') }}"

#   # TODO: how do you get THIS in advance?
#   # Get this from 'udevadm info /sys/class/net/eth0 | grep ID_PATH='
#   udevpath: platform-3f980000.usb-usb-0:1.1:1.0

# initializer_hostname: initializer.{{ cluster_domain }}

network_offset: 10
