import sys
import urllib2
import json
sys.path.insert(0, "..")
import config as cfg
import utils


def run(world):
    line_below_should_be_fixed_and_this_will_trigger_an_exception = True
    f = urllib2.urlopen('TODO: GET THIS FROM CONFIG')
    v = f.read()
    # this is a dicionary { vid: {'name': 'vlanname'} } of known vlans (e.g. from an IPAM database)
    vlans = json.loads(v)
    freq = {}
    result = {}
    for vlan in vlans:
        freq = {}
        for dev in world:
            if int(vlan) in world[dev]["vlans"]:
                name = world[dev]["vlans"][int(vlan)]["name"]
                if name in freq:
                    freq[name].append(dev)
                else:
                    freq[name] = [dev]
        if len(freq) == 0:
            # print "vlan does not appear on any known device"
            result[vlan] = (vlans[vlan]['name'], [])
            pass
        elif len(freq) > 1 or freq.keys()[0] != vlans[vlan]["name"]:
            print
            print
            print "VLAN", vlan
            print "vlan has multiple different names"
            sort = sorted(freq.items(), key=lambda(x): len(x[1]), reverse=True)
            result[vlan] = (vlans[vlan]['name'], sort)
            if vlans[vlan]['name'] not in freq:
                result[vlan][1].append((vlans[vlan]['name'], []))
            for v in sort:
                print len(v[1]), ":", "%-30s" % v[0], v[1],
                if v[0] == vlans[vlan]["name"]:
                    print "<<<<< FROM DB"
                else:
                    print
            if vlans[vlan]["name"] not in freq:
                print "From database:", vlans[vlan]["name"]
    utils.render_html(result, 'vlans_should_have_consistent_names.tpl', 'vlan_names.html')
