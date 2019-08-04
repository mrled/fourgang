Firewalld has caused me problems

"Error: INVALID_ZONE" when trying to modify firewall rules... fedora server has no default zone? Or did I do this to myself by trying to rename interfaces?
The default on a newly written sd card is FedoraServer, so maybe this is not going to be a problem going forward.

also if I disable firewalld on both client and server, TFTP works.
But it doesn't work if EITHER has it enabled.
(this is after i disabled ipv6)
(although i still see ipv6-to-4 addresses in syslog sometimes, no fucking idea why)

## Fedora minimal vs server

Minimal uses "public" as default zone.
Server uses "FedoraServer".
Argh.

## Useful commands:

    systemctl status firewalld

    # show default zone
    firewall-cmd --get-default-zone

    # allowed services
    firewall-cmd --list-services
    # allowed ports
    firewall-cmd --list-ports

    # show zones attached to interfaces
    firewall-cmd --get-active-zones

    # after modifying rules you MUST
    firewall-cmd --reload

