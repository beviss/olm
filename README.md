# OLM

A bunch of scripts designed primarily for some kind of "unit testing" of network infrastructure configuration.
After a while it evolved into a generic tool to pull and standardize operational information from various vendors network equipment.

## Modules
There are three types of modules in olm:
* data plugins,
* checks,
* renderers

**Data plugins** pull the relevant pieces of data from devices,
attempting to support all the nifty details of each vendor "standard" implementation. They perform this using protocols provided by
olm: SNMP, NETCONF and then plain SSH scraping. After all data plugins are ran, we end up with the "world", that is a dictionary,
where the keys are devices' hostnames and the values are dicts containing data prepared by data plugins. The idea is that the data format (schema) is consistent between all devices,
no matter which vendor it is from or which protocol was used to fetch this data.

**Checks** inspect this "world" dictionary to find errors in configuration. Some examples of checks are modules that:
* search for "up" switch ports that lack a description
* search for VPLS routers with peers that have no member ports of this VPLS
Checks should be written like standard software unit tests - they should test for one, well specified condition and return a list of violations.

**Renderers** differ from checks only by convention. They also work on the "world" dictionary, but are meant to render the data into HTML pages, for example to publish a pretty table with BGP sessions statistics.

