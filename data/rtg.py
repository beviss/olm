import sys
import xmltodict
import json
sys.path.insert(0, "..")
import config as cfg
from netconf_fetch import netconf_getconfig_raw


def key():
    return 'rtg'


def run(dev):
    rtg = []
    if dev.kind[:2] == ['juniper', 'ex']:
        print 'RTG: Downloading netconf config from:', dev.hostname
        dev_config = netconf_getconfig_raw(dev.hostname)
        dev_config = xmltodict.parse(dev_config)
        dev_config = dev_config['rpc-reply']['data']['configuration']
        if 'redundant-trunk-group' in dev_config['ethernet-switching-options']:
            rtg_groups = dev_config[
                'ethernet-switching-options']['redundant-trunk-group']['group']
            if type(rtg_groups) == dict:
                rtg_groups = [rtg_groups]
            for group in rtg_groups:
                g = {}
                g['name'] = group['name']
                g['ifaces'] = [i['name'] for i in group['interface']]
                rtg.append(g)
    return rtg
