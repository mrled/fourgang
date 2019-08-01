# egoboost files

The egoboost library directory.
These files are required for use of the egoboost.py script,
which duplicates and extends the functionality of sd_fusing.sh.

The firmware files are the official binary blobs required by hardkernel to boot the chip,
as well as an optional u-boot image and a script to "fuse" the files to an SD card for booting.
<https://github.com/hardkernel/u-boot/tree/odroidxu4-v2017.05/sd_fuse>

(Note that you can use an upsream u-boot image instead of the one from hardkernel.)

Additionally, the ego.uenv.txt is a U-Boot script installed by Ansible for cluster nodes.
