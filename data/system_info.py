import sys
sys.path.insert(0, "..")
import oids
import config as cfg
from netconf_fetch import netconf_rpc, netconf_getconfig
from snmpwalk import snmpwalk, Snmp_status


def key():
    return "system_info"


def autodetect_model_from_sysinfo_string(sysinfo):
    kind = 'unknown'
    if sysinfo.startswith('HP') or sysinfo.startswith('ProCurve'):
        return 'hp'
    elif 'Linux' in sysinfo:
        return 'linux'
    elif sysinfo.startswith('Juniper Networks, Inc MX-200'):
        return 'trapeze.wlc.200'
    # TODO more universal matching with regexps
    # ([a-z]\+)([0-9]+)(-[0-9][0-9][a-z])? groups: [0] -> type [1] -> model
    # [2] -> variant
    elif sysinfo.startswith('Juniper Networks'):
        kind = 'juniper'
        words = sysinfo.split()
        model = words[3]
        if model.startswith('ex'):
            kind += '.ex'
            kind += '.' + model[2:6]
        elif model.startswith('srx'):
            kind += '.srx'
            kind += '.' + model[3:]
        elif model.startswith('mx'):
            kind += '.mx'
            kind += '.' + model[2:]
        elif model.startswith('jsr'):
            kind += '.j'
            kind += '.' + model[3:]
        else:
            kind += '.unknown'
    elif sysinfo.startswith('Brocade'):
        kind = 'brocade'
        if sysinfo.startswith('Brocade MLX'):
            kind += '.mlx'
        elif 'ICX' in sysinfo:  # TODO ICX models detection
            kind += '.icx'
            for word in sysinfo.split():
                word = word.replace(',', '')
                # look for word looking like 'ICX6430-48' and extract '6430'
                if word.startswith('ICX') and len(word) >= 7:
                    after_icx = word[3:]
                    for model_part in after_icx.split('-'):
                        kind += '.' + model_part
                    break
    elif 'DGS-3100-24' in sysinfo:
        kind = 'dlink'
    elif sysinfo in ['SG300-10 10-Port Gigabit Managed Switch', '10-Port Gigabit Managed Switch']:
        kind = 'cisco.sb'
    else:
        print 'Unkown sysinfo string in model autodetection: ', sysinfo
    return kind


def run(dev):
    community = cfg.get("global", "community")
    snmp_version = cfg.get("global", "ver")
    print dev.hostname
    result = snmpwalk(snmp_version, community, dev.hostname, oids.sysDescr)
    if result.status == Snmp_status.OK:
        sys_info = result.objects[0].value
        print sys_info
        if dev.autodetect_model == True:
            dev.set_kind(autodetect_model_from_sysinfo_string(sys_info))
        return sys_info
    else:
        print 'nok'
        return 'unknown'
