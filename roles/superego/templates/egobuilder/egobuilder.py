#!/usr/bin/env python3

"""egoboost.py: Build U-Boot micro SD card images for ego machines

See also:
- https://blog.pcfe.net/hugo/posts/2019-01-27-fedora-29-on-odroid-hc2/
- https://blog.christophersmart.com/2018/04/28/fedora-on-odroid-hc1-mini-nas-armv7/
"""


import argparse
import os
import shutil
import stat
import subprocess
import sys
import textwrap

from urllib import request


# Constants that we get from the Jinja2 template
DEFAULT_EGOBUIDLER_LIB_DIRECTORY = "{{ egoboost_lib_directory }}"


class ProcMounts(object):
    """An interface to /proc/mounts

    The _mounts private member contains a list of dicts, each representing a line in /proc/mounts
    The names for the dict keys comes from fstab (see also 'man fstab')
    """

    _mounts = []

    @staticmethod
    def initialize():
        if ProcMounts._mounts:
            return
        with open('/proc/mounts') as pm:
            for line in pm.readlines():
                if not line:
                    continue
                # shlex.split() will split on whitespace, unless preceded by a backslash
                fs_spec, fs_file, fs_vfstype, fs_mntopts, fs_freq, fs_passno = shlex.split(line)
                ProcMounts._mounts.append(dict(
                    fs_spec=fs_spec, fs_file=fs_file, fs_vfstype=fs_vfstype, fs_mntopts=fs_mntopts,
                    fs_freq=fs_freq, fs_passno=fs_passno))

    @staticmethod
    def fsmounted(mountpoint):
        """Determine whether a path is a mountpoint
        """
        ProcMounts.initialize()
        for mount in ProcMounts._mounts:
            if mount['fs_file'] == mountpoint:
                return mount
        return None

    @staticmethod
    def devmounted(device):
        """Determine whether a device is mounted
        """
        ProcMounts.initialize()
        for mount in ProcMounts._mounts:
            if mount['fs_spec'] == device:
                return mount
        return None


def resolvepath(*path):
    if isinstance(path, tuple):
        path = list(path)
    elif not isinstance(path, str):
        path = [path]
    return os.path.realpath(os.path.normpath(os.path.expanduser(os.path.join(*path))))


def is_block_device(path):
    return stat.S_ISBLK(os.stat(path).st_mode)


def loopattach(diskimg):
    """Attach a disk image to a loop device, and return it
    """
    result = subprocess.run(['losetup', '--find', diskimg], check=True)
    return loopdev(diskimg)


def loopdev(diskimg):
    """If disk image is setup as a loop device, return loop device path
    """
    result = subprocess.run(
        ['losetup', '--all', '--list', '--json'], check=True, capture_output=True)
    for ld in json.loads(result.stdout.decode())['loopdevices']:
        if ld['back-file'] == diskimg:
            return ld['name']
    return None


def chrootscript(chrootpath, scriptpath):
    """Execute a script inside a chroot
    """
    chrooted_script = '/tmp/chrootscript.sh'
    shutil.copyfile(scriptpath, f'{chrootpath}{chrooted_script}')

    subprocess.run(['mount', '-t', 'proc', 'proc', f'{chrootpath}/proc'], check=True)
    try:
        subprocess.run(['mount', '--rbind', '/sys', f'{chrootpath}/sys'], check=True)
        try:
            subprocess.run(['mount', '--rbind', '/dev', f'{chrootpath}/dev'], check=True)
            try:
                subprocess.run(['chroot', chrootpath, '/bin/sh', chrooted_script], check=True)
            finally:
                subprocess.run(['umount', f'{chrootpath}/dev'], check=True)
        finally:
            subprocess.run(['umount', f'{chrootpath}/sys'], check=True)
    finally:
        subprocess.run(['umount', f'{chrootpath}/proc'], check=True)


def parseargs(*args, **kwargs):
    parser = argparse.ArgumentParser(
        "egobuilder - Build ego root filesystem for mounting as tmpfs")
    parser.add_argument(
        "--lib-directory", default=DEFAULT_EGOBUILDER_LIB_DIRECTORY, type=resolvepath,
        help=f"Location of default Fedora image(s); default is {DEFAULT_EGOBUILDER_LIB_DIRECTORY}")
    parser.add_argument(
        '--partition', default=3, type=int, help=(
            'Partition (of the baseimage) to use. '
            'Default images from Fedora have 3 partitions: 1=/boot/efi, 2=/boot, 3=/. '
            'We only need the root partition for cluster nodes, '
            'as they have retrieved kernel/initrd/dtb over TFTP. '
            'If the base image has no partitions, use "0".'))
    parser.add_argument(
        '--mountpoint', default='/tmp/egobuilder-tmp-root', help='Temporary mountpoint')
    parser.add_argument(
        'baseimage', help=(
            'Base image file, downloaded from a Fedora mirror; '
            'recomend starting with a minimal image. '
            'If not an absolute path, is relative to --lib-directory'))
    parsed = parser.parse_args()
    if not os.path.exists(parsed.baseimage):
        baseimage_abs = resolvepath(parsed.lib_directory, parsed.baseimage)
        if os.path.exists(baseimage_abs):
            parsed.baseimage = baseimage_abs
        else:
            raise Exception(
                f"Could not find baseimage {parsed.baseimage} "
                "absolutely or relative to . or --lib-directory")
    return parsed


def main(*args, **kwargs):
    parsed = parseargs(*args, **kwargs)

    loop = loopdev(parsed.baseimage)
    if not loop:
        loop = loopattach(parsed.baseimage)
    subprocess.run(['partprobe', loop], check=True)
    if parsed.partition == 0:
        loop_part = loop
    else:
        loop_part = f'{loop}{parsed.partition}'
    if not is_block_device(loop_part):
        raise Exception(f"Something is wrong; {loop_part} is not a block device")

    os.makedirs(parsed.mountpoint)

    fsmounted = ProcMounts.fsmounted(parsed.mountpoint)
    if fsmounted:
        raise Exception(f"{parsed.mountpoint} already mounted by {fsmounted['fs_spec']}")
    devmounted = ProcMounts.devmounted(loop_part)
    if devmounted:
        raise Exception(f"Loop device {loop_part} already mounted on {devmounted['fs_file']}")

    subprocess.run(['mount', loop_part, parsed.mountpoint], check=True)
    try:
        chrootscript()
    finally:
        subprocess.run(['umount', parsed.mountpoint], check=True)

if __name__ == '__main__':
    sys.exit(main(*sys.argv))
