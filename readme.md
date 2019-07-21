# FOURGANG: Home cluster project

FOURGANG: after a group intelligence called the Gang of Four from Peter Watt's Blindsight

## Networking concerns

The cluster will be on its own subnet, and will route to my home network.

I'll use 172.16.4.0/24 for the cluster network. I'm using a 192.168 subnet for my home network, but I don't think that's relevant for this

My home network will see fourgang.home.micahrl.com, which will point to an interface on the router.

The cluster will use the fourgang.micahrl.com subdomain (without the .home subdomain).

Take care to configure DNS for fourgang.home.micahrl.com however you normally do that.

## Network router - MicroTik hAP ac2

This thing was $60.
5x Gbe, one of which takes passive PoE.
2.4GHz and 5GHz wifi radio.

(I wanted flexibility because currently I need to use wifi to access the internet from my office.
Want to wire for ethernet, but probably will move first.)

Also cool

* Supoprts OpenWRT if I want
* Runs RouterOS (comes with a licensed copy)
* Has PoE input
* Extra Gbe ports might be useful as a switch.
* Switch chips have VLAN support per
  <https://wiki.mikrotik.com/wiki/Manual:Switch_Chip_Features#Introduction>,
  see also <https://wiki.mikrotik.com/wiki/Manual:Switch_Router>

Ansible has some rudimentary support:
<https://docs.ansible.com/ansible/latest/network/user_guide/platform_routeros.html>

### Initial manual configuration of the router

Goals:

* Secure the unit
  * Admin password, maybe user management
  * Firewall settings
* Configure appropriate interface to bridge to home network - in my case, using wifi
* Enable management over that interface as well
* Firmware updates as appropriate

Steps:

First, connect laptop to LAN ethernet port on router, configure for DHCP.

(My router came up as 192.168.88.1 - not sure if that's always the case or if its random or what.)

    ssh -l admin 192.168.88.1

We disable the admin user (`/user/disable 0`) because it has no password.

    /user add name=root group=full password="<some password>" disabled=no
    /user disable 0
    /user print

Now configure the wifi client

Note that wlan2 is my AC interface, and the ports 4,5 are the wlan1 and wlan2 interfaces.
For my config I remove them both from the default bridge.

	/interface bridge remove port 4,5
	/ip dhcp-client add interface=wlan2 disabled=no
	/interface wireless security-profiles add mode=dynamic-keys name=<SSID>_profile authentication-types=wpa2-psk wpa2-pre-shared-key="<SSID key>"
	/interface wireless set wlan2 mode=station ssid=<SSID> security-profile=<SSID>_profile
	/interface wireless registration-table print

Allow SSH on the wifi interface.
Making this priority 4 means it is processed before the rejections.
(See `/ip firewall filter print`.)

	/ip firewall filter add action=accept chain=input protocol=tcp port=22 disabled=no place-before=4

Get latest firmware

	/system package update install

Upload the SSH key and enable it.
This might need to be RSA or DSA... lol.

	# From your host
	scp ~/.ssh/id_rsa.pub root@<Mikrotik hostname>
	
	# From the router
	/user ssh-keys import user=root public-key-file=id_rsa.pub

Misc stuff

* See MAC addresses of wifi interfaces: `/interface wireless print`
* See MAC addresses of ethernet interfaces: `/interface ethernet print`

## Initial Ansible configuration

I'm using Ansible 2.8

* See ansible.cfg
* See .vault-pass-script

Vault pass script lets the ansible vault auto get its password if your GPG keychain is unlocked.
Create a .vault-pass file with something like

	openssl rand -hex 64 | gpg --encrypt --output .vault-passphrase.gpg --recipient '<YOUR GPG EMAIL ADDRESS>'
	
Run `ansible-vault create VAULT-FILENAME` to create the vault the first time;
run `ansible-vault edit VAULT-FILENAME` to edit it later.


## Configure the router from Ansible

* Generally ensure router is secure
* Disable unneeded service (`/ip services print`)
* Configure Ethernet ports properly

This is all done via Ansible.

Some pre-steps:

* Set host vars etc
* Create a vault in host_vars/mikrotik/fourgang.micahrl.com/vault.yml and put the Mikrotik root password in it...
  for smoe reason the private key isn't working.

Now just do:

	ansible-playbook mikrotik.yml

TODO: Ansible appears to be SUPER slow with the mikrotik. No idea why.

## Configure the home network

In order to allow packets to flow, you must configure your home network to route 192.168.4.0/24 through the IP address it assigns to the Mikrotik.
This is different for every router, so you'll have to figure this out yourself.
(Some routers might not allow this at all, idk. I use a Unifi USG at home and it is configured in the controller under settings -> routing & firewall.)

Once this is done, if you connect a laptop to one of the ethernet ports on the Mikrotik and give it a static IP of 192.168.4.anything, it should be able to reach the Internet.

TODO: Would it be better to use NAT? That way the parent network doesn't have to know anything about the fourgang network. Easier to transport my cluster for showing off.

# The initializer

hostname: psyche.fourgang.micahrl.com

Role: net booting the cluster nodes, keeping serial logs from conserver

Implementation:
* Raspberry pi b 2 because that's the ARM system I had lying around (I also already had a USB TTL cable for the Pi)
* doing this new I might use an ODROID XU4Q, since it's based on the same platform as the HC2 boards that are my cluster nodes
* 4x USB UART cables for ODROID
* A powered USB2 hub I had lying around that runs on 5v
* One downside is that the rpi and USB2 hub run on 5V, while the rest of my cluster runs on 12V. This means I need either a separate powersupply, some kind of step down board for each device, or to use wall warts. I went with the last option for now.

### Initial configuration

Configuration of this is MANUAL, meaning we do a regular Fedora install and configure the rpi over its serial with a USB TTL cable.
We need one manually configured machine to host the network configuration.

* write the SD card per instructions
  * https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi
  * https://docs.fedoraproject.org/en-US/quick-docs/raspberry-pi/
* I used balenaEtcher on macOS
* connect RPI and go through first boot - create root password, configure wired network to 172.16.4.10/24
  For this, you will need a USB TTL serial cable to talk to the rpi
  (or a keyboard/monitor I guess).

I installed like this.

TODO: I wonder if I could use some Live USB support, where it doesn't write to the disk, for this?
Would make configuration easier in case of rpi hardware failure.

TODO: Include links to other docs, other options.
Linux on these ARM boards is weird.
My preference is to use as much mainline/upstream code as possible.

Prepare the card from an existing Fedora install.
Note that this is specifically for the rpi2 - the rpi3 needs a different console argument,
and other ARM boards like the Odroid HC2 we will configure later need other differences.

The device path for my SD card:

	sdcard=/dev/sdb

Prepare the card:

	sudo fedora-arm-image-intaller --target=rpi2 --image=Fedora-Server-armhfp-30-1.2.sda.raw.xz --norootpass -resizefs --args "console=tty0 console=ttyAMA0,115200" --media="$sdcard"
	
Mount the card to apply serial configuration:

	mkdir /mnt/sdcard1
	mount "${sdcard}1" /mnt/sdcard1
	mv /mnt/sdcard1/config.txt /mnt/sdcard1/config.txt.dist
	sed 's/# enable_uart=1/enable_uart=1/' /mnt/sdcard1/config.txt.dist > /mnt/sdcard1/config.txt
	umount /mnt/sdcard1

Then insert the SD card into the RPI2
Connect TTL serial (TODO: guide for this),
and also Ethernet and power.

Connect the USB TTL cable to a Mac or Linux machine, and open the serial port.
(Look in `/dev/tty*` for the USB UART; mine is called tty.usbserial.)

	screen /dev/tty.usbserial 115200

The machine should boot.
The first screen you see should be the initial config screen where you can do things ilke create users, set up initial networking, etc:

    ================================================================================
    ================================================================================
    1) [x] Language settings                 2) [x] Time settings
           (English (United States))                (America/New_York timezone)
    3) [ ] Network configuration             4) [!] Root password
           (Connecting...)                          (Password is not set.)
    5) [!] User creation
           (No user will be created)

    Please make a selection from the above ['c' to continue, 'q' to quit, 'r' to
    refresh]:

I configured a root password and networking.
I will leave other settings to Ansible.

Networking configured like so:

Device configuration

    1) IPv4 address or "dhcp" for DHCP
       192.168.4.10
    2) IPv4 netmask
       255.255.255.0
    3) IPv4 gateway
       192.168.4.1
    4) IPv6 address[/prefix] or "auto" for automatic, "dhcp" for DHCP, "ignore" to
       turn off
       auto
    5) IPv6 default gateway
    6) Nameservers (comma separated)
       1.1.1.1,1.0.0.1
    7) [x] Connect automatically after reboot
    8) [x] Apply configuration in installer
    
I was unable to configure the hostname here, but we can configure it later.

	ssh-copy-id root@192.168.4.10


## TODOs

### Renaming interfaces

Ugh, what a fucking mess. Why is systemd like this.

From here: https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/, it says:

> You create your own manual naming scheme, for example by naming your interfaces "internet0", "dmz0" or "lan0". For that create your own .link files in /etc/systemd/network/, that choose an explicit name or a better naming scheme for one, some, or all of your interfaces. See systemd.link(5) for more information.

Based on that, I think something like my `roles/initializer/templates/10-fourgang-ifname.link.j2` would work.
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

