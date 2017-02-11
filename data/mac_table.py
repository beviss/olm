import sys
sys.path.insert(0, "..")
import oids
import config as cfg
import utils
from snmpwalk import snmpwalk, Snmp_status
from netconf_fetch import netconf_getconfig

# return data format
# [{'mac': 'ff:00:ff:00:ff:00', 'ifIndex': 123, 'vlan': 48}]


def key():
    return "mac_table"


def require():
    return ['ifaces']


def run(dev):
    community = cfg.get("global", "community")
    snmp_version = cfg.get("global", "ver")

    oid_to_check = oids.dot1qTpFdbPort

    result = []
    response = snmpwalk(snmp_version, community, dev.hostname, oid_to_check)
    port_ids = snmpwalk(snmp_version, community, dev.hostname, oids.dot1dBasePortIfIndex)
    port_ids = utils.index_dict(port_ids.objects)
    port_ids = {int(k): int(v) for k,v in port_ids.items()}
    port_ids[0] = 0
    
    # vlan ids in qbridge mib ARE NOT vlan tags
    # we need to convert those ids to actual tags:
    #   - for HP ProCurve we need another table from Q-BRIDGE: the dot1qVlanCurrentTable
    #   - for juniper switches we need the mapping from jnxExVlanTag
    vlan_ids = {}
    if dev.kind_prefix(['hp']):
        fdb_ids = snmpwalk(snmp_version, community, dev.hostname, oids.dot1qVlanFdbId)
        vlan_ids = utils.index_dict_reverse(fdb_ids.objects)
    elif dev.kind_prefix(['juniper', 'ex']):
        fdb_ids = snmpwalk(snmp_version, community, dev.hostname, oids.jnxExVlanTag)
        vlan_ids = utils.index_dict(fdb_ids.objects)
    vlan_ids = {int(k): int(v) for k,v in vlan_ids.items()}
    print vlan_ids
    if response.status == Snmp_status.OK:
        for o in response.objects:
            print o.oid[-6:]
            mac = ':'.join(map(lambda x: "%0.2X" % x, o.oid[-6:]))
            print o.oid, o.value
            vlan_fdb_id = o.oid[-7]
            vlan = vlan_ids[vlan_fdb_id]
            if_index = port_ids[int(o.value)]
            # if_index == 0 means flood address or internal interface mac or
            # other internal stuff
            if if_index != 0 and mac != '00:00:00:00:00':
                result.append({'mac': mac, 'ifIndex': if_index, 'vlan': vlan})
    print result
    print [r for r in result if r['vlan'] in [4000, 500]]
    return result
