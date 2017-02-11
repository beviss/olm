import sys
sys.path.insert(0, "..")
import oids
import config as cfg
from snmpwalk import snmpwalk
from netconf_fetch import netconf_getconfig


def key():
    return "vlans"


def run(dev):
    community = cfg.get("global", "community")
    snmp_version = cfg.get("global", "ver")

    result = {}

    # HP

    if dev.kind_prefix(['hp']):
        #names = snmpwalk(snmp_version, community, dev.hostname, oids.ifNameOid)
        names = snmpwalk(snmp_version, community, dev.hostname, oids.dot1qVlanStaticName)
        #descrs = snmpwalk(snmp_version, community, dev.hostname, oids.ifDescrOid)

        joined = {}

        for iface in names.objects:
            result[iface.oid[-1]] = {"name": iface.value}

    ################
    # JUNIPER EX
    ################
    elif dev.kind_prefix(['juniper', 'ex']):
        names = snmpwalk(snmp_version, community, dev.hostname, oids.jnxExVlanName)
        tags = snmpwalk(snmp_version, community, dev.hostname, oids.jnxExVlanTag)
        for vlan in tags.objects:
            result[int(vlan.value)] = {"name": [v for v in names.objects if v.oid[-1] == vlan.oid[-1]][0].value[1:-1]}

    ################
    # JUNIPER MX
    ################
    elif dev.kind_prefix(['juniper', 'mx']):
        conf = netconf_getconfig(dev.hostname)
        ifs = conf.xpath('//rpc-reply/data/configuration/interfaces/interface')
        for i in ifs:
            units = i.xpath('unit')
            for u in units:
                vlan_tag = u.xpath('vlan-id')
                vlan_name = u.xpath('description')
                if len(vlan_tag) == 0:
                    continue
                if len(vlan_name) == 0:
                    name = ''
                else:
                    name = vlan_name[0].text
                tag = int(vlan_tag[0].text)
                result[tag] = {'name': name}

    ################
    # BROCADE
    ################
    elif dev.kind_prefix(['brocade']):
        names = snmpwalk(snmp_version, community, dev.hostname, oids.snVLanByPortCfgVLanName)
        for vlan in names.objects:
            result[int(vlan.oid[-1])] = {"name": vlan.value[1:-1]}
    for vid, data in result.items():
        if len(data['name']) > 0:
            if data['name'][0] == '"' and data['name'][-1] == '"':
                data['name'] = data['name'][1:-1]
    return result
