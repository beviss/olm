import ConfigParser
import sys
import os
import yaml
import fnmatch

config_file_name = 'main.cfg'

cfg = None
cfg2 = None


class OlmConfig(dict):

    def __get(self, mapping, query):
        pass

    def __init__(self, config_path='./config.yaml', defaults_path='./defaults.yaml', secrets_path='./secrets.yaml'):
        """ Create

        config_path: source of configuration data. If path to a file, then read file. If path to a directory, read all files ending with .conf. If glob, read all files matched by glob
        defaults_path: source of default values for config. Syntax is the sama as config_path
        """
        self.config = {}
        self.defaults = {}
        self.secrets = {}
        self.config_path = config_path
        self.defaults_path = defaults_path
        self.load()

    def __expand_paths(self, paths):
        return paths
        expanded = []
        for p in paths:
            if os.path.isfile('s'):
                pass

    def __load(self, mapping, path):
        mapping.clear()
        if type(path) == list:
            paths = path
        else:
            paths = [path]
        for path in paths:
            if os.path.isfile(path):
                with open(path, 'r') as config_file:
                    partial = yaml.load(config_file)
                    mapping.update(partial)

        expanded = self.__expand_paths(paths)
        if len(expanded) == 0:
            print "Empty config: no files to read"
        pass

    def load(self, config_path=None, defaults_path=None, secrets_path=None):
        if config_path is None:
            config_path = self.config_path
        self.__load(self.config, config_path)

    def __match_host(self, host_def, host):
        return fnmatch.fnmatch(host, pattern=host_def)

    def get_secret(self, realm, target):
        """realm: either ssh, snmp, netconf
           target: hostname or ip"""
        for secret in [s for s in secrets if s['realm'] == realm]:
            if self.__match_host(secret['host'], target):
                return secret

    def get(self, query):
        parts = query.split(':')
        mapping = self.config
        for part in parts:
            mapping = mapping.get(part, {})
        return mapping

    def set(self, query, value):
        parts = query.split(':')
        mapping = self.config
        for part in parts[:-1]:
            mapping = mapping.get(part, {})
        mapping[parts[-1]] = value

    def reload(self):
        return self.load()


def init(config_path='./config.yaml'):
    global cfg
    # print 'Reading config from', config_file_name
    #cfg = ConfigParser.ConfigParser()
    #success = cfg.read(config_file_name)
    cfg = OlmConfig(config_path)
    cfg.load()
    # if len(success) == 0:
    #  print 'Invalid config file'
    #  sys.exit(0)

#init()


def get(section, value):
    global cfg
    return cfg.get(section + ':' + value)


def get_list(section, value):
    entry = get(section, value)
    return entry
    try:
        entry = get(section, value)
    except ConfigParser.NoOptionError:
        return []
    items = entry.split(',')
    result = []
    for i in items:
        strip = i.strip()
        if len(strip) > 0:
            result.append(strip)
    return result


def set(section, key, value):
    global cfg
    cfg.set(section, key, value)
