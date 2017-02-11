import sys
sys.path.insert(0, "..")
import oids
import utils
import config as cfg
from snmpwalk import snmpwalk


def key():
    return 'mpls'


def run(dev):
    if dev.kind_prefix(['brocade', 'mlx']):
        community = cfg.get('global', 'community')
        snmp_version = cfg.get('global', 'ver')

        ldp_router_id = snmpwalk(
            snmp_version, community, dev.hostname, oids.mplsLdpLsrId)
        router_id = utils.ipv4_address_from_snmp_hex_string(
            ldp_router_id.objects[0].value)
        return {'router_id': router_id}
