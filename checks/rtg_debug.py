
def run(world):
    for dev in world:
        print
        print dev
        dev = world[dev]
        if len(dev['rtg']) > 0:
            print 'has rtg:'
            print dev['rtg']
