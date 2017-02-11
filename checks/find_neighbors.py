import sys
sys.path.insert(0, "..")
import utils
import config as cfg


def run(world):
    mismatch = {}
    processed = set()
    accepted_port_types = ['ethernetCsmacd', 'ieee8023adLag']

    for dev_name, dev in world.items():
        print dev_name.upper()
        n_dict = {}
        neighbors = []
        nset = set()
        for (ifIndex, iface) in [x for x in dev['ifaces'].items() if x[1]['type'] in accepted_port_types]:
            neighbor = utils.get_neighbor_name(iface['descr'])
            if neighbor:
                nset.add(neighbor)
        for n in nset:
            shortest_end_description = None
            shortest_end_description_length = 9999999
            for iface in dev['ifaces'].values():
                for word in iface['descr'].split():
                    if len(word) < shortest_end_description_length and '::' + n in word:
                        shortest_end_description_length = len(word)
                        shortest_end_description = iface
            neighbors.append((n, shortest_end_description['ifIndex']))
            n_dict[n] = shortest_end_description['ifIndex']
        dev['neighbors'] = n_dict
