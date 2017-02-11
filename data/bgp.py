import sys
import ast
sys.path.insert(0, "..")
import config as cfg
from netconf_fetch import netconf_rpc
import lxml


def key():
    return 'bgp'

""" Return data structure description:
[
      address = peer ip address
      as = peer AS-NUM
      description = session description
      state = state
      advertised = # of advertised prefixes
      received = # of received prefixes
      accepted = # of installed prefixes
      active = # of active prefixes
      suppressed = # of ??????
      group = juniper bgp configuration group
      elapsed-time = seconds since last state change
]
"""


def run(dev):
    final = []
    if dev.model == 'juniper':
        print 'BGP: Downloading bgp neighbor:', dev.hostname
        bgp = netconf_rpc(dev.hostname, '<get-bgp-neighbor-information></get-bgp-neighbor-information>')
        print 'get-bgp-neighbor-information'
        peers = bgp.xpath('//rpc-reply/bgp-information/*')
        result = {}
        for peer in peers:
            current = {}
            # print lxml.etree.tostring(peer, pretty_print=True)
            print "=============== PEER END"
            current['address'] = peer.xpath('peer-address')[0].text.split('+')[0]
            current['as'] = peer.xpath('peer-as')[0].text
            desc = peer.xpath('description')
            if len(desc) > 0:
                current['description'] = desc[0].text
            else:
                current['description'] = 'UNKNOWN'
            current['state'] = peer.xpath('peer-state')[0].text
            adv_pref = peer.xpath('bgp-rib/advertised-prefix-count')
            if len(adv_pref) > 0:
                current['advertised'] = int(adv_pref[0].text)
            else:
                current['advertised'] = 0
            rec_pref = peer.xpath('bgp-rib/received-prefix-count')
            if len(rec_pref) > 0:
                current['received'] = int(rec_pref[0].text)
            else:
                current['received'] = 0
            acc_pref = peer.xpath('bgp-rib/accepted-prefix-count')
            if len(acc_pref) > 0:
                current['accepted'] = int(acc_pref[0].text)
            else:
                current['accepted'] = 0
            sup_pref = peer.xpath('bgp-rib/suppressed-prefix-count')
            if len(sup_pref) > 0:
                current['suppressed'] = int(sup_pref[0].text)
            else:
                current['suppressed'] = 0
            # print current
            result[current['address']] = current
        print 'get-bgp-summary-information'
        bgp_sum = netconf_rpc(dev.hostname, '<get-bgp-summary-information></get-bgp-summary-information>')
        peers = bgp_sum.xpath('//rpc-reply/bgp-information/bgp-peer')
        print lxml.etree.tostring(bgp_sum, pretty_print=True)
        for peer in peers:
            current = {}
            # print lxml.etree.tostring(peer, pretty_print=True)
            current['address'] = peer.xpath('peer-address')[0].text
            current['elapsed-time'] = int(peer.xpath('elapsed-time')[0].get('seconds'))
            current['active'] = ''.join(peer.xpath('bgp-rib/active-prefix-count/text()'))
            result[current['address']].update(current)
            pass
        bgp_group = netconf_rpc(dev.hostname, '<get-bgp-group-information></get-bgp-group-information>')
        groups = bgp_group.xpath('//rpc-reply/bgp-group-information/bgp-group')
        # print lxml.etree.tostring(bgp_group, pretty_print=True)
        for group in groups:
            name = group.xpath('name')[0].text
            peers = group.xpath('peer-address')
            for peer in peers:
                # print lxml.etree.tostring(peer, pretty_print=True)
                address = peer.text.split('+')[0]
                result[address]['group'] = name
        for data in result.values():
            final.append(data)
    return final
