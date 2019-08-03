# Renaming interfaces

Ugh, what a fucking mess. Why is systemd like this.

From here: https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/, it says:

> You create your own manual naming scheme, for example by naming your interfaces "internet0", "dmz0" or "lan0". For that create your own .link files in /etc/systemd/network/, that choose an explicit name or a better naming scheme for one, some, or all of your interfaces. See systemd.link(5) for more information.

Based on that, I think something like my `10-fourgang-ifname.link.j2` would work.
HOWEVER, apparently you have to put that in initramfs - investigate this for the images I'm building.
(https://askubuntu.com/questions/783457/renaming-network-interface-in-ubuntu-16-04-with-systemd-fails)

The stupid way is to use `ip`: https://unix.stackexchange.com/questions/205010/centos-7-rename-network-interface-without-rebooting

	/sbin/ip link set eth1 down
	/sbin/ip link set eth1 name eth123
	/sbin/ip link set eth123 up

In Ansible we cannot rename the NICs, but they can be done this way:

	cat > /etc/systemd/network/10-fourgang-ifname.link <<EOF
	[Match]
	MACAddress=b8:27:eb:73:d2:86

	[Link]
	Name=GANG4
	EOF

	dracut --force

(You might have to move an existing initramfs out of the way first.)

