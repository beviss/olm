from collections import defaultdict
import sys
sys.path.append('..')
import utils


def run(world):
    report_peers_as_hostnames = True
    joined = defaultdict(dict)
    # make mapping of routerids to device data objects
    possible_peers = {}
    for dev_name, dev in world.items():
        if 'vpls' in dev:
            print dev_name
            print [v for vpls, v in dev['vpls'].items() if 'peers' not in v]
        if 'mpls' in dev:
            possible_peers[dev['mpls']['router_id']] = dev
    for dev_name, dev in world.items():
        # mapping { vpls_id => {name: ..., nonsense_peers: [(ip, reason)]}}
        problems = {}
        for vpls_id, vpls in dev.get('vpls', {}).items():
            nonsense_peers = []
            if len(vpls['egress']) == 0:
                nonsense_peers.append(('', 'No local egress ports'))
            if len(vpls['peers']) == 0:
                nonsense_peers.append(('', 'No peers'))
            else:
                for peer in vpls['peers']:
                    if peer not in possible_peers:
                        print '[ERROR] [checks/vpls_peers_should_have_egress_ports] Device has a VPLS peer that is not in our database!'
                        nonsense_peers.append((peer, '500: address unknown in local peer table'))
                    else:
                        peer_vpls = possible_peers[peer][
                            'vpls'].get(vpls_id, None)
                        if report_peers_as_hostnames:
                            peer_label = possible_peers[peer]['dev'].name
                        else:
                            peer_label = peer
                        if peer_vpls is None:
                            nonsense_peers.append((peer_label, 'Missing VPLS'))
                        elif len(peer_vpls['egress']) == 0:
                            nonsense_peers.append(
                                (peer_label, 'No egress ports'))
            if len(nonsense_peers) > 0:
                problems[vpls_id] = {'name': vpls['name'], 'nonsense_peers': nonsense_peers}
        if len(problems) > 0:
            joined[dev_name] = problems
    # print joined
    utils.render_html(joined, 'vpls_peers_should_have_egress_ports.tpl', 'nonsense_vpls_peers.html')
