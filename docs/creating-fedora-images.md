<https://fedoraproject.org/wiki/Architectures/ARM/F28/Installation#Initial-setup>

From the FAQ:

How do I use Fedora ARM when I have no serial cable or display?

Though not recommended it is possible to use Fedora ARM without a serial cable or display. When doing so you may want to limit updates to reduce the possibility of not being able to boot. (This example is from a Fedora 27 system, you may need to adjust the mounts used).

	USER= # your user account
	sudo rm /run/media/$USER/__/etc/systemd/system/graphical.target.wants/initial-setup-graphical.service  #only needed for Desktop images
	sudo rm /run/media/$USER/__/etc/systemd/system/multi-user.target.wants/initial-setup.service
	sudo mkdir /run/media/$USER/__/root/.ssh/
	cat /home/$USER/.ssh/id_rsa.pub | sudo tee -a /run/media/$USER/__/root/.ssh/authorized_keys
	sudo chmod -R u=rwX,o=,g= /run/media/$USER/__/root/.ssh/

How do I enlarge the root partition?

The images include cloud-utils-growpart to enlarge the root partition, then resize2fs/xfs_growfs to use that newly available space.

    # STEP 1: enlarge the 4th partition (this example uses mmcblk0)
    growpart /dev/mmcblk0 4
    # STEP 2: grow the fileystem to fill the available space (all images except Server)
    resize2fs /dev/mmcblk0p4
    # OR STEP 2: for the server image (which uses xfs)
    xfs_growfs /dev/mmcblk0p4
