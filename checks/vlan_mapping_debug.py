import sys
sys.path.insert(0, "..")


def run(world):
    for dev in world:
        print
        print dev.upper()
        dev = world[dev]

        print dev['vlan_mapping']
