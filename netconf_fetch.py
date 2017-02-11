from ncclient.xml_ import *
from ncclient import manager
from lxml import etree
import cache
from config import cfg


def netconf_getconfig_raw(hostname, user=None, password=None):
    print 'netconf_getconfig', hostname,
    if cfg.get('global:read_cache'):
        cached = cache.cache.get_netconf_cfg(hostname)
        if cached:
            print '...from cache'
            return cached
    print
    credentials = cfg.get_secret('netconf', hostname)
    password = credentials['password']
    user = credentials['username']
    if password is None or password == '':
        return '<xml></xml>'
    mgr = manager.connect(host=hostname, port=22, username=user, password=password, timeout=10, device_params={'name': 'junos'}, hostkey_verify=False)
    conf = mgr.get_config('running')
    mgr.close_session()
    if cfg.get('global:write_cache'):
        cache.cache.put_netconf_cfg(hostname, conf.tostring)
    return conf.tostring


def netconf_getconfig(hostname, user=None, password=None):
    result = netconf_getconfig_raw(hostname, user, password)
    xml = etree.fromstring(result)
    return xml


def netconf_rpc_raw(hostname, method, user=None, password=None):
    print 'netconf_rpc', hostname,
    if cfg.get('global:read_cache'):
        cached = cache.cache.get_netconf_rpc(hostname, method)
        if cached:
            print '...from cache'
            return cached
    print
    credentials = cfg.get_secret('netconf', hostname)
    password = credentials['password']
    user = credentials['username']
    if password is None or password == '':
        return '<xml></xml>'
    mgr = manager.connect(host=hostname, port=22, username=user, password=password, timeout=10, device_params={'name': 'junos'}, hostkey_verify=False)
    result = mgr.rpc(method)
    mgr.close_session()
    if cfg.get('global:write_cache'):
        cache.cache.put_netconf_rpc(hostname, method, result.tostring)
    return result.tostring


def netconf_rpc(hostname, method, user=None, password=None):
    result = netconf_rpc_raw(hostname, method, user, password)
    xml = etree.fromstring(result)
    return xml
