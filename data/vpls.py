import sys
import socket
sys.path.insert(0, "..")
import oids
import utils
import config as cfg
from snmpwalk import snmpwalk
from collections import defaultdict


def key():
    return 'vpls'


def run(dev):
    joined = {}
    if dev.kind_prefix(['brocade', 'mlx']):
        community = cfg.get('global', 'community')
        snmp_version = cfg.get('global', 'ver')

        names = snmpwalk(snmp_version, community, dev.hostname, oids.vplsConfigName)
        ids = snmpwalk(snmp_version, community, dev.hostname, oids.fdryVplsVcId)
        ports = snmpwalk(snmp_version, community, dev.hostname, oids.fdryVplsEndPoint2VlanTagMode)

        pw_ids = snmpwalk(snmp_version, community, dev.hostname, oids.pwID)
        pw_peers = snmpwalk(snmp_version, community, dev.hostname, oids.pwPeerAddr)

        vpls_index_id_dict = utils.index_dict(ids.objects)

        peer_addrs = utils.join_snmp_results_by_last_oid_segment(pw_ids.objects, pw_peers.objects)
        peer_addrs = map(lambda (x, y): (int(x), utils.ipv4_address_from_snmp_hex_string(y)), peer_addrs)
        # dict: { VPLS_ID -> LIST OF PEERS (ips as strings) }
        peer_addrs = utils.list_of_pairs_to_dict_of_lists(peer_addrs)

        vlan_tags = {}

        for (vpls_id, vpls_name) in utils.join_snmp_results_by_last_oid_segment(ids.objects, names.objects):
            vpls_id = int(vpls_id)
            peer_addrs_hostnames = []
            for peer in peer_addrs[vpls_id]:
                try:
                    hostname = socket.gethostbyaddr(peer)[0]
                    print hostname
                    peer_addrs_hostnames.append(hostname)
                except Exception as e:
                    print 'Error getting reverse DNS record for VPLS peer', peer, e
            joined[vpls_id] = {'name': vpls_name, 'egress': [], 'peers': peer_addrs[vpls_id], 'peers_hostnames': peer_addrs_hostnames}
        print peer_addrs
        print joined

        for port in ports.objects:
            internal_vpls_id = port.oid[-5]
            vpls_id = int(vpls_index_id_dict[internal_vpls_id])
            egress_vlan = port.oid[-4]
            iface_id = port.oid[-1]
            joined[vpls_id]['egress'].append(
                (egress_vlan, iface_id, port.value == '1'))

        for vpls_id, vpls in joined.items():
            tags = set([e[0] for e in vpls['egress']])
            if len(tags) != 1:
                print 'Unexpected number of egress vlan tags for VPLS ID', vpls_id, 'on', dev.hostname, ':', tags

    return joined
