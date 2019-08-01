My goal is to netboot the Odroid XU4 platform (including Odroid HC1 and Odroid HC2) with Das U-Boot.

I want to have a mostly static boot drive that contains only U-Boot and required firmware files like trustzone etc crap from Odroid.

It should be configured to boot over the network using servers retrieved from DHCP.

* Use UEnv.txt to configure U-boot: https://linux-sunxi.org/UEnv.txt
* It can be used for tftp booting: http://u-boot.10912.n7.nabble.com/Can-DHCP-be-used-for-TFTP-booting-td29627.html
* An example of configuring UEnv.txt here: http://www.orangepi.org/Docs/Settingup.html
* Advanced U-Boot stuff: https://github.com/umiddelb/armhf/wiki/Get-more-out-of-%22Das-U-Boot%22
  * notes on how partitions work and why some are hidden
  * userland access
* U-boot Linux kernel with NFS root: https://wiki.odroid.com/troubleshooting/nfsboot
* Official U-Boot docs for the Xu4 platform: https://gitlab.denx.de/u-boot/u-boot/blob/master/doc/README.odroid
* using U-Boot with TFTP boot with statically configured TFTP server: https://www.linuxjournal.com/content/handy-u-boot-trick
* guide from hardkernel, BUT NOTE, 'boot.ini' is only in their u-boot fork; I want to use upstream uboot and uEnv.txt instead https://wiki.odroid.com/odroid-xu4/application_note/software/pxe_boot
