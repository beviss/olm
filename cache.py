import config as cfg
import datetime
import pickle
import traceback


class Cache():

    def __init__(self):
        self.time = datetime.datetime.now()
        self.snmp = {}        # hostname : { oid : [ results ] }
        self.netconf_cfg = {}  # hostname : string
        self.netconf_rpc = {}  # hostname : { rpc_request : string }

    def is_expired(self, snmp_response):
        return False

    def get_snmp(self, hostname, oid):
        if hostname in self.snmp:
            if oid in self.snmp[hostname]:
                response = self.snmp[hostname][oid]
                if not self.is_expired(response):
                    return response
        return None

    def put_snmp(self, snmp_response):
        if snmp_response.hostname not in self.snmp:
            self.snmp[snmp_response.hostname] = {}
        snmp_response.cached = True
        self.snmp[snmp_response.hostname][
            snmp_response.query_oid] = snmp_response

    def get_netconf_cfg(self, hostname):
        if hostname in self.netconf_cfg:
            return self.netconf_cfg[hostname]
        return None

    def put_netconf_cfg(self, hostname, cfg):
        self.netconf_cfg[hostname] = cfg

    def get_netconf_rpc(self, hostname, request):
        if hostname in self.netconf_rpc:
            if request in self.netconf_rpc[hostname]:
                return self.netconf_rpc[hostname][request]
        return None

    def put_netconf_rpc(self, hostname, request, reply):
        if hostname not in self.netconf_rpc:
            self.netconf_rpc[hostname] = {}
        self.netconf_rpc[hostname][request] = reply


def load_from_file(filename):
    f = open(filename, 'r')
    cache = pickle.load(f)
    print 'Loaded cache from ', filename, 'resulting type:', type(cache)
    return cache


def dump_to_file(filename, cache):
    f = open(filename, 'w')
    pickle.dump(cache, f)
    print 'Dumped cache to', filename


def load():
    filename = cfg.get('global', 'cache_file')
    return load_from_file(filename)


def dump(cache):
    filename = cfg.get('global', 'cache_file')
    return dump_to_file(filename, cache)

cache = None


def init():
    global cache
    try:
        cache = load()
    except Exception as e:
        print type(e)
        # traceback.print_stack()
        cache = Cache()
