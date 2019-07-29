On my rpi2, I had lots of system time issues.

The most frustrating wasn't obvious. I had been working with the system, and rebooted it. When it came back, nothing was logging to `/var/log/messages` or `journalctl -xe`.

The problem turned out to be the lack of a real time clock, and network errors that prevented the Pi from syncing NTP on boot.

I tried several things to fix:

First, `timedatectl set-ntp true`. That didn't appear to do anything.

Then, add NTP servers to the list in `/etc/systemd/timesyncd.conf`, `systemctl daemon-reload`, `timedatectl set-ntp false`, `timedatectl set-ntp true`. This didn't appear to change behavior either.

Finally, I set the time approximately correct with `timedatectl`, and then restarted it. That put it to, as far as I could tell, completely correct.

Happily, logging worked. again.

(I guess we can't do something as simple as append to a fucking file in /var/log, oh no, that would be too fucking easy)

It might also be that BIND cannot resolve addresses with DNSSEC?
I'm not sure, but BIND definitely had trouble during this as well.
