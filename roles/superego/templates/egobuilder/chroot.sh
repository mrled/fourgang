#!/bin/sh
set -eu

usage() {
    cat <<ENDUSAGE
Usage: $0 [PATH]
Chroot into PATH after mounting required filesystems like /dev and /proc
ENDUSAGE
}

path=
while test $# -gt 0; do
    case "$1" in
        -h | --help ) usage; exit;;
        *) path="$1"; shift;;
    esac
done
        
mount -t proc proc "$path/proc/"
mount --rbind /sys "$path/sys/"
mount --rbind /dev "$path/dev/"

chroot "$path" /bin/sh
