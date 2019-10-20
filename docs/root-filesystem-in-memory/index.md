# Root filesystem in memory

Linux supports several different types of RAM-backed filesystem.
<https://www.kernel.org/doc/Documentation/filesystems/ramfs-rootfs-initramfs.txt>

Based on the above, I think we want to use a "tmpfs" for our root filesystem.
It should be limited to some reasonably small size.
Maybe 256MB if we can get the system that small -
remember, these devices only have 2GB of RAM.

I think we can get there from here:
<http://www.espenbraastad.no/posts/centos-7-rootfs-on-tmpfs/>
