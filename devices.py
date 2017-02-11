import json
import urllib2
import socket
import config as cfg


class Dev():
    # test if given list of strings is a prefix of this device's kind

    def kind_prefix(self, pfx):
        if not self.kind or type(pfx) != list:
            return False
        if len(self.kind) < len(pfx):
            return False
        return all(map(lambda x: x[0] == x[1], zip(self.kind, pfx)))

    # syntax: ? matches any (single) module, * matches any number of modules
    # examples:
    #   kind_match(['juniper', '*']) is the same as kind_prefix(['juniper'])
    # TODO
    # TODO: extend to regexps
    def kind_match(self, match_list):
        return False

    def set_kind(self, kind):
        if type(kind) == list:
            self.model = kind[0]
            self.kind = kind
        else:
            self.model = kind
            if kind:
                if '.' in kind:
                    self.kind = kind.split('.')
                else:
                    self.kind = [kind]
            else:
                self.kind = None

    def __init__(self, hostname=None, kind=None, autodetect_model=True, name=None):
        self.hostname = hostname
        if name is not None:
            self.name = name 
        else: # set name based on hostname
            try:
                socket.inet_pton(socket.AF_INET, hostname)
                # we have an IP address as hostname
                self.name = hostname
            except AttributeError:
                if hostname is not None and '.' in hostname:
                    self.name = hostname.split('.')[0]
                else:
                    self.name = hostname
        self.autodetect_model = autodetect_model
        self.set_kind(kind)

    def __str__(self):
        return str({'name': self.name, 'hostname': self.hostname, 'model': self.model, 'kind': self.kind})

    def __repr__(self):
        return self.__str__()


def read_dev_file(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    devices = []
    for l in lines:
        l = l.strip()
        if len(l) == 0:
            continue
        if l[0] == '#':
            continue
        record = l.split()
        if len(record) < 2:
            continue
        hostname = record[0].strip()
        kind = record[1].split('.')
        kind = map(lambda s: s.strip(), kind)
        name = None
        if len(record) > 2:
            name = record[2]
        if len(hostname) == 0:
            continue
        for k in kind:
            if len(k) == 0:
                continue
        devices.append(Dev(hostname, kind, name=name))
    return devices


def read_dev_url(url):
    response = urllib2.urlopen(url)
    response_body = response.read()
    raw_list = json.loads(response_body)
    devices = []
    for dev in raw_list:
        if 'name' and 'address' in dev:
            d = Dev()
            d.hostname = dev['address']
            d.name = dev['name']
            if 'model' in dev:
                d.model = dev['model']
            devices.append(d)
    return devices


def get_dev_list():
    source = cfg.get('devices', 'dev_source')
    default_type = 'hp'
    dev_list = []
    name_blacklist = cfg.get_list('devices', 'name_blacklist')
    if source == 'config':
        hostnames = cfg.get_list('devices', 'devs')
        types = [s.split('.') for s in cfg.get_list('devices', 'types')]
        dev_list = [Dev(h[0], h[1]) for h in zip(hostnames, types)]
    elif source == 'rancidfile':
        filename = cfg.get('devices', 'rancidfile')
        rancidfile = open(filename, 'r')
        lines = rancidfile.readlines()
        for l in lines:
            if len(l.strip()) > 0:
                record = l.split(':')
                if record[2].startswith('up'):
                    dev_list.append(Dev(record[0], [record[1]]))
    elif source == 'file':
        filename = cfg.get('devices', 'file')
        dev_list = read_dev_file(filename)
    elif source == 'url':
        url = cfg.get('devices', 'url')
        dev_list = read_dev_url(url)
    else:
        raise Exception('Unknown devices source in the config file: ' + str(source))
    # leave only the devices which names do not contain strings from the
    # blacklist
    dev_list = [d for d in dev_list if not any(
        [name in d.hostname for name in name_blacklist])]
    print dev_list
    return dev_list
