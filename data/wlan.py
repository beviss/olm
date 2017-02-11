import sys
sys.path.insert(0, "..")
import oids
import config as cfg
from snmpwalk import snmpwalk

# TRAPEZE WLAN DATA


def key():
    return 'wlan'


def strip_quotes(s):
    if len(s) >= 2:
        if s[0] in ['"', '\''] and s[-1] in ['"', '\'']:  # strip quotes
            return s[1:-1]
    return s


def run(dev):
    if not dev.kind_prefix(['trapeze', 'wlc', '200']):
        return {}

    community = cfg.get('global', 'community')
    snmp_version = cfg.get('global', 'ver')

    ap_names = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApName)
    ap_locations = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApLocation)
    ap_serials = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApSerial)
    ap_models = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApModel)
    ap_ips = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApIp)
    ap_users = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApUsers)
    ap_nums = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApNum)
    ap_services = snmpwalk(snmp_version, community, dev.hostname, oids.wlanApService)

    joined = {}
    for ap_id in ap_nums.objects:
        apid = int(ap_id.value)
        if apid not in joined:
            joined[apid] = {}
        joined[apid]['oid'] = ap_id.oid[-6:]
        for ap in ap_names.objects:
            if ap.oid[-6:] == ap_id.oid[-6:]:
                joined[apid]['name'] = strip_quotes(ap.value)
        for ap in ap_locations.objects:
            if ap.oid[-6:] == ap_id.oid[-6:]:
                joined[apid]['location'] = ap.value
        for ap in ap_serials.objects:
            if ap.oid[-6:] == ap_id.oid[-6:]:
                joined[apid]['serial'] = ap.value
        for ap in ap_ips.objects:
            if ap.oid[-6:] == ap_id.oid[-6:]:
                joined[apid]['ip'] = ap.value
        for ap in ap_users.objects:
            if ap.oid[-6:] == ap_id.oid[-6:]:
                joined[apid]['users'] = ap.value

    for ap in ap_locations.objects:
        if ap.oid[-1] in joined:
            location = strip_quotes(ap.value)
            joined[ap.oid[-1]]['location'] = location
    return joined
