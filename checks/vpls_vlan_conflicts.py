import sys
sys.path.insert(0, "..")


def run(world):
    for dev in world:
        dev_name = dev
        dev = world[dev]
        if 'vpls' in dev and 'vlans' in dev:
            print 'Checking VPLS-VLAN conflicts for', dev_name
            common = (set(dev['vpls'].keys())).intersection(
                set(dev['vlans'].keys()))
            if len(common) > 0:
                print 'Conflicting IDs:', common
