import sys
sys.path.insert(0, "..")
import json
import oids
import config as cfg
from netconf_fetch import netconf_rpc, netconf_getconfig, netconf_rpc_raw
from snmpwalk import snmpwalk
import xmltodict
import ifaces as data_ifaces


def key():
    return "vlan_mapping"


def hexstring_to_id_list(s):
    s = s.lower()
    offset = 0
    blockoffset = 0
    ids = []
    for ch in s:
        offset = blockoffset * 4 + 4
        try:
            mask = int(ch, 16)
            while mask > 0:
                if mask % 2 == 1:
                    ids.append(offset)
                mask = mask / 2
                offset -= 1
            blockoffset += 1
        except ValueError:
            pass
    return ids


def run(dev):
    community = cfg.get('global', 'community')
    snmp_version = cfg.get('global', 'ver')

    joined = {}

    print 'Getting vlan-port mappings from', dev.hostname

    ############
    # Brocade
    ############
    if dev.kind_prefix(['brocade']):
        mapping = snmpwalk(snmp_version, community, dev.hostname, oids.snVLanByPortMemberTagMode)

        for entry in mapping.objects:
            if len(entry.oid) > 1:
                ifIndex = entry.oid[-1]
                vlan_tag = entry.oid[-2]
                tagged = (entry.value == '1')
                if ifIndex not in joined:
                    joined[ifIndex] = {}
                joined[ifIndex][vlan_tag] = tagged
    ############
    # HP
    ############
    elif dev.kind_prefix(['hp']):
        mapping = snmpwalk(snmp_version, community,
                           dev.hostname, oids.dot1qVlanCurrentEgressPorts)
        untagged_mapping = snmpwalk(
            snmp_version, community, dev.hostname, oids.dot1qVlanCurrentUntaggedPorts)
        for vlan in mapping.objects:
            vlan_tag = vlan.oid[-1]
            ifaces = hexstring_to_id_list(vlan.value)
            for iface in ifaces:
                if not iface in joined:
                    joined[iface] = {}
                joined[iface][vlan_tag] = True
        for vlan in untagged_mapping.objects:
            vlan_tag = vlan.oid[-1]
            ifaces = hexstring_to_id_list(vlan.value)
            for iface in ifaces:
                if not iface in joined:
                    joined[iface] = {}
                joined[iface][vlan_tag] = False
    ############
    # Juniper EX
    ############
    elif dev.kind_prefix(['juniper', 'ex']):
        mapping = netconf_rpc(
            dev.hostname, '<get-vlan-information><extensive/></get-vlan-information>')
        #mapping_raw = netconf_rpc_raw(dev.hostname, '<get-vlan-information><extensive/></get-vlan-information>')
        # print json.dumps(xmltodict.parse(mapping_raw), indent=4)
        vlans = mapping.xpath('//rpc-reply/vlan-information/vlan')
        ifs = {}
        for v in vlans:
            tag = v.xpath('vlan-tag')[0].text
            tag = int(tag)
            members = v.xpath(
                'vlan-detail/vlan-member-list/vlan-member/vlan-member-interface')
            tagness = v.xpath(
                'vlan-detail/vlan-member-list/vlan-member/vlan-member-tagness')
            for (i, t) in zip(members, tagness):
                iface_name = i.text.split('.')[0]  # ignore unit number
                tagged = (t.text == 'tagged')
                if iface_name not in ifs:
                    ifs[iface_name] = {}
                ifs[iface_name][tag] = tagged
        # convert mapping from (name -> vlans) to (ifIndex -> vlans)
        ifs2 = data_ifaces.run(dev)
        new_map = {}
        # i - interface name, m - { vlan : tagness }
        for (i, m) in ifs.items():
            ifs3 = [(x, y) for (x, y) in ifs2.items() if y[
                'name'] == i]  # x - ifIndex, y - iface_obj
            if len(ifs3) == 1:
                new_map[ifs3[0][0]] = m
            else:
                print 'Error while finding interface with name ==', i, ':', ifs3
        joined = new_map
    ##############
    # Juniper MX
    ##############
    elif dev.kind_prefix(['juniper', 'mx']):
        conf = netconf_getconfig(dev.hostname)
        ifs = conf.xpath('//rpc-reply/data/configuration/interfaces/interface')
        mapping = {}
        for i in ifs:
            name = i.xpath('name')[0].text
            vlans = i.xpath('unit/vlan-id')
            if len(vlans) > 0:
                mapping[name] = {}
            for v in vlans:
                tag = int(v.text)
                mapping[name][tag] = True
        joined = mapping

    return joined
