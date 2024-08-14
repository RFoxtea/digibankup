**Digibankup** is a simple backup utility for the Digibank part of
[ECOSO Mechelen](https://ecoso.be/).

It performs a backup of the following:

* The FOG Project server

In the future it may also perform a backup for the following:

* The SnipeIT server
* The LendEngine server

It also tracks if a backup has already been performed recently, and foregoes
another backup if this is the case.

**Example usage:** `python3.12 -m digibankup --config voorbeeld.ini`

`voorbeeld.ini` contains sample configuration (in Dutch). This will explain
the usage of the program.

Also try `python3.12 -m digibankup --help` for explanation of possible
commandline arguments.
