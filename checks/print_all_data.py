import pprint


def run(world):
    pp = pprint.PrettyPrinter(indent=4)
    for dev in world:
        print "===================="
        print str(dev)
        pp.pprint(world[dev])
