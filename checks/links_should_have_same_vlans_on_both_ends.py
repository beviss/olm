import sys
import datetime
import re
sys.path.insert(0, "..")
import utils
import config as cfg


def dependencies():
    return {'checks': ['find_neighbors'], 'data': []}


def difference_code((vlan_id, (local, remote))):
    code = None
    if local == 'X' and remote != 'X':
        code = 1
    elif local != 'X' and remote == 'X':
        code = 2
    elif local != 'X' and remote != 'X':
        if local != remote:
            code = 0
        else:
            code = 3
    return code * 10000 + vlan_id

accepted_port_types = ['ethernetCsmacd', 'ieee8023adLag']


def get_iface_by_name(dev, iface_name, world):
    found = [i for i in world[dev]['ifaces'].values() if i['name'] == iface_name]
    if len(found) > 1:
        print 'Assertion failed: unexpected number of interfaces with name', iface_name, len(found)
        return None
    elif len(found) == 0:
        return None
    else:
        return found[0]


def find_adjacent_iface(dev, iface_id, world):
    neighbor_name = utils.get_neighbor_name(
        world[dev]['ifaces'][iface_id]['descr'])
    if not neighbor_name:
        return None
    if neighbor_name not in world:
        print 'Neighbor', neighbor_name, 'of', dev, 'does not exist in our world'
        return None
    possible_ends = [x for x in world[neighbor_name]['ifaces'].values() if dev in x['descr'] and x['type'] in accepted_port_types]
    if len(possible_ends) == 0:
        print "No candidates for adjacent ports found in neighbor", neighbor_name, 'of', dev
        return None
    iface_with_shortest_description = None
    shortest_end_description_length = 9999999
    missing = []
    for e in possible_ends:
        for word in e['descr'].split():
            if len(word) < shortest_end_description_length and dev in word:
                shortest_end_description_length = len(word)
                iface_with_shortest_description = e
        print ' possible other end on', neighbor_name, '>', e['name'], e['descr']
    chosen = iface_with_shortest_description
    print ' chosen:', chosen['name'], chosen['descr']
    return (neighbor_name, chosen)


def run(world):
    # rewrite juniper vlan_mapping to be indexed by ifindex, not iface name
    for dev in world:
        if len(world[dev]['vlan_mapping'].keys()) > 0:
            if type(world[dev]['vlan_mapping'].keys()[0]) == str:  # correct juniper ifnames
                new_map = {}
                # i - interface name, m - { vlan : tagness }
                for (i, m) in world[dev]['vlan_mapping'].items():
                    ifs = [(x, y) for (x, y) in world[dev]['ifaces'].items() if y['name'] == i]  # x - ifIndex, y - iface_obj
                    if len(ifs) == 1:
                        new_map[ifs[0][0]] = m
                world[dev]['vlan_mapping'] = new_map
        #    print new_map
    # the real work starts here
    mismatch = {}
    processed = set()
    # regexp to recognize '::' port descriptions
    uplink_rexp_pattern = '.*(::[a-z0-9-]+).*'
    uplink_rexp = re.compile(uplink_rexp_pattern)

    for dev_name, dev in world.items():
        # merge vpls data with vlan data
        if 'vpls' in dev:
            for (vpls_id, vpls) in dev['vpls'].items():
                egress = vpls['egress']
                for (vlan_id, iface_id, tagged) in egress:
                    if iface_id not in dev['vlan_mapping']:
                        dev['vlan_mapping'][iface_id] = {}
                    dev['vlan_mapping'][iface_id][vlan_id] = tagged

    for dev_name, dev in world.items():
        print dev_name.upper()

        errors = {}
        for neighbor_name, local_ifid in dev['neighbors'].items():
            if neighbor_name in processed:
                break
            print dev_name, 'has neighbor', neighbor_name, 'on port', dev['ifaces'][local_ifid]['name']
            if neighbor_name not in world:
                print 'but we cant find him...'
                continue
            end = find_adjacent_iface(dev_name, local_ifid, world)
            if not end:
                print 'error?'
                continue
            end = end[1]
            neighbor = world[neighbor_name]
            remote_ifid = end['ifIndex']
            local_mapping = {}
            local_vlans = set()
            remote_mapping = {}
            remote_vlans = set()
            if local_ifid in dev['vlan_mapping']:
                local_mapping = dev['vlan_mapping'][local_ifid]
                local_vlans = set(local_mapping.keys())
            if remote_ifid in neighbor['vlan_mapping']:
                remote_mapping = neighbor['vlan_mapping'][remote_ifid]
                remote_vlans = set(remote_mapping.keys())
            all_vlans = local_vlans.union(remote_vlans)

            mapping = []
            mismatch_found = False
            for vlan in all_vlans:
                local = 'X'
                if vlan in local_mapping:
                    local = 'T' if local_mapping[vlan] else 'U'
                remote = 'X'
                if vlan in remote_mapping:
                    remote = 'T' if remote_mapping[vlan] else 'U'
                mapping.append((vlan, (local, remote)))
                if local != remote:
                    mismatch_found = True
            if mismatch_found:
                mapping.sort(key=difference_code)
                print local_ifid
                adjacency_descriptor = (dev_name, neighbor_name, dev['ifaces'][local_ifid]['name'], end['name'])
                print adjacency_descriptor
                mismatch[adjacency_descriptor] = mapping
        processed.add(dev_name)
    utils.render_html(mismatch, 'links_should_have_same_vlans_on_both_ends.tpl', 'vlan_mismatches.html')
    rtgs = []
    for dev_name, dev in world.items():
        for rtg in dev.get('rtg', []):
            groupname = rtg['name']
            dev_names = [dev_name]
            port_names = [('Master port', 'Slave port')]
            vlans = [{}]
            vlan_names = dev['vlans']
            print rtg
            for iface_name in rtg['ifaces']:
                iface_name = str(iface_name.split('.')[0])
                iface = get_iface_by_name(dev_name, iface_name, world)
                vlans[0] = dev['vlan_mapping'][iface['ifIndex']]
                # print world[neighbor_name]['vlan_mapping']
                (neighbor_name, adjacent_iface) = find_adjacent_iface(dev_name, iface['ifIndex'], world)
                dev_names.append(neighbor_name)
                port_names.append((iface_name, adjacent_iface['name']))
                r_vlans = world[neighbor_name]['vlan_mapping'][adjacent_iface['ifIndex']]
                vlans.append(r_vlans)
                vlan_names.update(world[neighbor_name]['vlans'])
            all_vlans = set()
            for v in vlans:
                all_vlans.update(v.keys())
            group = [groupname, dev_names, port_names, vlans, sorted(list(all_vlans)), vlan_names]
            rtgs.append(group)
    utils.render_html({'rtgs': rtgs, 'date': datetime.datetime.now().isoformat()}, 'links_should_have_same_vlans_on_both_ends_rtg.tpl', 'vlan_mismatches_rtg.html')
    print mismatch
