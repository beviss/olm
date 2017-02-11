import sys
sys.path.insert(0, "..")
import oids
import config as cfg
from snmpwalk import snmpwalk
import json


def key():
    return 'ifaces'

blacklist = ['linux']


def run(dev):
    community = cfg.get("global", "community")
    snmp_version = cfg.get("global", "ver")

    if dev.model in blacklist:
        return {}

    names = snmpwalk(snmp_version, community, dev.hostname, oids.ifNameOid)
    updown = snmpwalk(snmp_version, community, dev.hostname, oids.ifOperStatusOid)
    descrs = snmpwalk(snmp_version, community, dev.hostname, oids.ifDescrOid)
    types = snmpwalk(snmp_version, community, dev.hostname, oids.ifTypeOid)
    macs = snmpwalk(snmp_version, community, dev.hostname, oids.ifPhysAddress)

    joined = {}

    for iface in names.objects:
        if iface.oid[-1] not in joined:
            joined[iface.oid[-1]] = {"name": iface.value,
                                     "ifIndex": iface.oid[-1]}
            joined[iface.oid[-1]]['type'] = 'unknown'
        else:
            raise Exception("duplicate iface id!")

    for iface in updown.objects:
        if iface.oid[-1] not in joined:
            #print joined
            #print str(iface.oid[-1])
            continue
            raise Exception("non-matching iface id! :" + str(iface.oid[-1]))
        else:
            joined[iface.oid[-1]]["up"] = (iface.value == "up(1)")

    for iface in descrs.objects:
        if iface.oid[-1] not in joined:
            #print joined
            #print str(iface.oid[-1])
            continue
            raise Exception("non-matching iface id!")
        else:
            descr = iface.value
            joined[iface.oid[-1]]["descr"] = iface.value

    for iface in types.objects:
        if iface.oid[-1] not in joined:
            #print joined
            #print str(iface.oid[-1])
            continue
            raise Exception("non-matching iface id!")
        else:
            val = iface.value.split('(')
            if len(val[0]) > 0:
                val = val[0]
                joined[iface.oid[-1]]["type"] = val

    for iface in macs.objects:
        if iface.oid[-1] not in joined:
            #print joined
            #print str(iface.oid[-1])
            continue
            raise Exception("non-matching iface id!")
        else:
            joined[iface.oid[-1]]['mac'] = iface.value.upper()

    for ifindex, iface in joined.items():
        if 'descr' not in iface:
            iface['descr'] = '<<unknown description>>'

    print "IFACE LIST FOR ", dev.hostname
    for ifIndex in sorted(joined.keys()):
        print ifIndex, ":", joined[ifIndex]

    return joined
