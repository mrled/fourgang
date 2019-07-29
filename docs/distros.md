# Distros

I started with Fedora because we use it at work and the rpi4 had just shipped and Fedora supported it out of the box, so I thought I might use it more going forward. However, I somewhat regret this.

* harder to automate package installtion - you can automate dpkg-select (or whatever its called), but RPM has no equivalent
* it seems to have a *deeply* confused networking story (initscripts network-scripts, networkmanager, and optional systemd-networkd)
* fedora-arm-image-intaller can't like... configure first boot options. what.

Also, it's fucking slow on the rpi2 I have.

Considerations:

- Debian 10 shipped after rpi4 was released but before mine even arrived in the mail
- Alpine is tiny and maybe faster? and surely has a better networking story.
