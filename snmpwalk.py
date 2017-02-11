#!/usr/bin/env python
import subprocess as sub
import datetime
import cache
import config as cfg


def execute_process(args):
    output = sub.Popen(args, stdout=sub.PIPE,
                       stderr=sub.STDOUT).communicate()[0]
    return output


class Snmp_status:
    OK = (0, 'ok')
    MISSING_OID = (1, 'missing oid')
    UNKNOWN_HOST = (2, 'unknown host')
    TIMEOUT = (3, 'timeout')

stats = {}

# holds snmp response along with query data
# query_oid - the oid used in request
# hostname - the target hostname
# status - the status of the query (see class snmp_status for pissible values)
# objects - the snmp objects returned from the target (None if status != OK)


class Snmp_response:

    def __init__(self, query_oid, hostname, status, objects, timestamp=None, cached=False):
        if status != Snmp_status.OK:
            assert len(objects) == 0
        self.query_oid = query_oid
        self.hostname = hostname
        self.status = status
        self.objects = objects
        if timestamp is None:
            self.timestamp = datetime.datetime.now()
        else:
            self.timestamp = timestamp
        self.cached = cached


class Snmp_object:

    def __init__(self, oid, value_type, value):
        self.oid = oid
        self.value_type = value_type
        self.value = value

    def __repr__(self):
        return "<OID: " + str(self.oid) + ", type: " + str(self.value_type) + ", value: " + str(self.value) + ">"

    def __eq__(self, other):
        return (self.oid, self.value_type, self.value) == (other.oid, other.value_type, other.value)

    def __hash__(self):
        return hash((self.oid, self.value_type, self.value))


def snmp_object_from_snmpwalk_line(line):
    fields = line.split()
    oid = map(int, fields[0][1:].split('.'))
    value_type = fields[2][:-1]
    if 'No Such Instance' in line:
        value = None
    else:
        value = ' '.join(fields[3:])
    # numerical oid without leading dot, value type without trailing colon, remaining part is the value
    o = Snmp_object(oid, value_type, value)
    return o


def update_stats(response):
    global stats
    if response.status != Snmp_status.OK:
        if not response.hostname in stats:
            stats[response.hostname] = {}
        if not response.status in stats[response.hostname]:
            stats[response.hostname][response.status] = []
        stats[response.hostname][response.status].append(response.query_oid)


def snmpwalk(ver, community, hostname, oid, timeout=1.5, retries=2):
    print "snmpwalk:", hostname, oid,
    if cfg.get('global', 'read_cache'):
        cached = cache.cache.get_snmp(hostname, oid)
        if cached:
            print '...from cache'
            update_stats(cached)
            return cached
    output = execute_process(["snmpwalk", "-t", str(timeout), "-r", str(retries), "-v", ver, "-c", community, "-On", hostname, oid])
    objects = []
    if "No Response" in output:
        status = Snmp_status.TIMEOUT
    elif "No Such Object" in output:
        status = Snmp_status.MISSING_OID
    elif "Unknown host" in output:
        status = Snmp_status.UNKNOWN_HOST
    else:
        status = Snmp_status.OK
        objects_tmp = output.splitlines()
        for line in objects_tmp:
            if line.startswith('.'):
                objects.append(line)
            else:
                objects[-1] = objects[-1] + line
        objects = map(snmp_object_from_snmpwalk_line, objects)
    response = Snmp_response(oid, hostname, status, objects)
    print "snmpwalk status:", status, len(objects)
    if cfg.get('global', 'write_cache'):
        cache.cache.put_snmp(response)
        cache.dump(cache.cache)
    update_stats(response)
    return response

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print "Usage: snmpwalk.py [SNMP version] [COMMUNITY] [HOSTNAME] [OID]"
        sys.exit()
    print snmpwalk(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
