# Netbooting the XU4 platform with U-Boot

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

## What happens during a net boot

Setting the stage:

I have a private network with a DHCP and TFTP server.
The MAC address of the booting node is added to the TFTP server,
which provides an IP address and the location of a kernel via TFTP.

I have other files,
like a root image straight from Fedora
and a device tree (.dtb) required for booting an ARM kernel,
but I haven't configured access to them.
So the boot log will show nothing except loading the kernel.

The kernel and other files I have are from a Fedora mirror via
<http://download.fedoraproject.org/pub/fedora/linux/releases/30/Server/armhfp/os/images/pxeboot>.

I then inserted an SD card, created a 1GB VFAT partition,
ran `mkfs.vfat`,
and "fused" the card based on instructions from Hardkernel.
The VFAT filesystem starts at cylinder 2048;
earlier cylinders are used for the bootloader stages 1 and 2, U-Boot, and TrustZone.
I wrote a U-Boot `uEnv.txt` to the VFAT partition that looked like this:

    netretry=yes
    uenvcmdx=setenv bootdelay 5; echo "Bootstrap our brain from the hive mind"; setenv netretry yes; dhcp ${kloadaddr}; tftpboot ${fdtaddr} /armhfp.f30.vmlinuz; setenv bootargs console=tty1 console=ttySAC2,115200n8 cpuidle.off=1 rd.driver.pre=ledtrig-heartbeat,xhci-plat-hcd no_bL_switcher; bootm ${kloadaddr} - ${fdtaddr}
    uenvcmd=run uenvcmdx

The bootloader stages and TrustZone must be obtained from Hardkernel.
In facgt, the first stage of the bootloader must be signed.
Hardkernel also provides U-Boot,
but a build of the upstream open source project works fine;
I used the U-Boot from Fedora's `uboot-images-armv7` pacakge.

Boot log: <./20190731-1951-first-tftp-boot-log.txt>

In that log, it tries to load the following files from TFTP:

    > grep Filename 20190731-1951-first-tftp-boot-log.txt
    Filename '/armhfp.f30.vmlinuz'.
    Filename '/pxelinux.cfg/C0A80415'.
    Filename '/pxelinux.cfg/C0A8041'.
    Filename '/pxelinux.cfg/C0A804'.
    Filename '/pxelinux.cfg/C0A80'.
    Filename '/pxelinux.cfg/C0A8'.
    Filename '/pxelinux.cfg/C0A'.
    Filename '/pxelinux.cfg/C0'.
    Filename '/pxelinux.cfg/C'.
    Filename '/pxelinux.cfg/default-arm-exynos'.
    Filename '/pxelinux.cfg/default-arm'.
    Filename '/pxelinux.cfg/default'.
    Filename 'boot.scr.uimg'.
    Filename '/armhfp.f30.vmlinuz'.
    Filename 'dtb/exynos5422-odroidhc1.dtb'.

The `armhfp.f30.vmlinuz` filename it tries first comes from DHCP.
`dhcpd` has a `host` stanza that looks like this:

    host ego01.fourgang.micahrl.com {
      option host-name "ego01.fourgang.micahrl.com";
      hardware ethernet 00:1e:06:36:84:0c;
      fixed-address 192.168.4.21;
      next-server 192.168.4.10;
      filename "/armhfp.f30.vmlinuz";
    }

Some notes about the remaining queries:

* The pxelinux stuff is looking for something
  * https://github.com/lentinj/u-boot/blob/master/doc/README.pxe
  * It has most of the functionality of actual pxeilnux
  * <https://wiki.syslinux.org/wiki/index.php?title=Doc/pxelinux>
  * looks like this is the *IP address* in upper case hex
  * this checks out; when I plug it into an online hex->ipv4 address converter, it returns the correct 192.168.4.21 address
  * and when it doesn't find any file with that name, it tries the same name minus the least significant digit
  * after that it tries a couple of default files
* boot.scr.uimg looks like a compiled U-Boot "script" image. Not sure why we'd need one of those, since we are using uEnv.txt
* Then it loads the kernel again? Not sure why it does this, but judging by the log, it is successful
* It tries to find a device tree file on TFTP but can't

I'm not actually sure what does this.
Maybe the kernel is looking for all those places by default?
Maybe U-Boot?

TODO: I really want it to just reboot and try again (maybe after waiting a minute or two) when boot fails.

OK, what happens if I get the dtb file that is being requested under dtb/ ?
(Can retrieve it from the same Fedora mirror I get the kernel from.)

<./20190731-2228-second-tftp-boot-log.txt>

It boots more! But not by much.

Useful list of kernel command lines, to better understand options we append:
<https://www.kernel.org/doc/html/v4.14/admin-guide/kernel-parameters.html>

uEnv.txt:

    netretry=yes
    uenvcmdx=setenv bootdelay 5; echo "Bootstrap our brain from the hive mind"; setenv netretry yes; dhcp ${kloadaddr}; tftpboot ${fdtaddr} /armhfp.f30.vmlinuz; setenv bootargs console=tty1 console=ttySAC2,115200n8 cpuidle.off=1 rd.driver.pre=ledtrig-heartbeat,xhci-plat-hcd no_bL_switcher; bootm ${kloadaddr} - ${fdtaddr}
    uenvcmd=run uenvcmdx

pxelinux.cnf/default:

    menu title FOURGANG BOOTSTRAPPER
    timeout 50
    default fourgang tftp debug

    label fourgang tftp
        kernel armhfp.f30.vmlinuz
        append console=console=tty1 console=ttySAC2,115200n8 cpuidle.off=1 rd.driver.pre=ledtrig-heartbeat,xhci-plat-hcd no_bL_switcher ip=${ipaddr}:${serverip}:${gatewayip}:${netmask}
        fdt dtb/exynos5422-odroidhc1.dtb
        initrd armhfp.f30.initrd

    label fourgang tftp debug
        kernel armhfp.f30.vmlinuz
        append console=console=tty1 console=ttySAC2,115200n8 cpuidle.off=1 rd.driver.pre=ledtrig-heartbeat,xhci-plat-hcd no_bL_switcher ip=${ipaddr}:${serverip}:${gatewayip}:${netmask} debug earlyprintk
        fdt dtb/exynos5422-odroidhc1.dtb
        initrd armhfp.f30.initrd

It boots the kernel!!

<./20190802-0948-third-tftp-boot-log-kernel-boots.txt>

A note about u-boot, pxelinux, and tftp:
U-Boot can boot a kernel from TFTP directly, but can only be configured with ONE.
Its support for PXELINUX lets you define a boot menu with multiple options.
In order to allow separate production and debug kernel configurations,
or test a new OS (kernel, root fs, whateve),
and in order to allow prompting a user to select a different boot configuration,
I think we have to use the PXELINUX config file.

What I'm confused about is why we specify the kernel in the uEnv.txt AND in PXELINUX config.
The first of those might not be necessary.

Ok, so the above boot log complained about passing ip= to the kernel.
We can just use DHCP to get an IP address once the system boots;
i think passing the ip to the kernel from U-Boot is useful for an NFS root situation,
but that's not what we're going for here.
Let's remove it.

<./20190802-1001-fourth-tftp-boot-log-kernel-boots-emergency-mode.txt>

AW SHIT, IT BOOTS TO EMERGENCY MODE! THIS IS REALLY FUCKING GOOD NEWS.


Some side notes and TODO: items:

* dtb == device tree bindings
* if you don't want to buy the usb uarts, you could probably use NetConsole support frmo U-Boot:
  <https://github.com/u-boot/u-boot/blob/master/doc/README.NetConsole>
* might be worth understanding autoboot more thoroughly to make booting as reliable as possible:
  <https://github.com/u-boot/u-boot/blob/master/doc/README.autoboot>
* we might not ACTUALLY need pxelinux support for boot menus?
  * <https://github.com/u-boot/u-boot/blob/master/doc/README.bootmenu>
  * <https://github.com/u-boot/u-boot/blob/master/doc/README.menu>
  * I guess doing this the PXELINUX way lets the boot server control it - not uenv.txt, which is harder to update
* dns support? ,https://github.com/u-boot/u-boot/blob/master/doc/README.dns>
* If I stop the boot process and set environment variables in U-Boot, is it writing them back to the card? Do they persist?

Trying this in uEnv.txt:

    netretry=yes
    bootdelay=10
    autoload=yes
    autostart=yes
    uenvcmdx=echo "Bootstrap our brain from the hive mind"; dhcp ${kloadaddr};
    uenvcmd=run uenvcmdx

that appeared to work

But wait. It never shows my "Bootstrap our brain message"

jesus fuck. i just tried again with out a uEnv.txt at all (but it does have an empty VFAT partition)
and it boots all the way like before.
WELP.
