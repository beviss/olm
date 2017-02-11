from collections import defaultdict
import config as cfg
import jinja2
import re

# returns string ip address
def ipv4_address_from_snmp_hex_string(hex_string):
    octets = hex_string.split()
    octets = map(lambda x: str(int(x, 16)), octets)
    ip_str = '.'.join(octets)
    return ip_str

# input -> [('a', 1), ('a', 2), ('b', 3)]
# output -> { 'a': [1, 2], 'b': [3] }
def list_of_pairs_to_dict_of_lists(pairs):
    result = defaultdict(list)
    for pair in pairs:
        result[pair[0]].append(pair[1])
    return result

# WIP
def join_snmp_table(columns, snmp_results):
    """columns: dict of columns {index, name}
       snmp_results: list of snmp result lists
    """
    joined = defaultdict(dict)
    for row in snmp_results:
        column_id = row.oid[-2]
        row_id = row.oid[-1]
        if column_id not in columns:
            continue
        else:
            column_name = columns[column_id]
            joined[row_id][column_name] = row.value
    return joined

# returns list of pairs: (value, value) joined by the same last oid
# segment from two snmp queries
def join_snmp_results_by_last_oid_segment(results_left, results_right, left_segment_index=-1, right_segment_index=None):
    if right_segment_index == None:
        right_segment_index = left_segment_index
    dict_left = index_dict(results_left, left_segment_index)
    joined = []
    for result in results_right:
        joined.append((dict_left[result.oid[right_segment_index]], result.value))
    return joined

# returns dictionary mapping oid segment to value
def index_dict(snmp_results, segment_index=-1):
    dict_left = {}
    for result in snmp_results:
        dict_left[result.oid[segment_index]] = result.value
    return dict_left

def index_dict_reverse(snmp_results, segment_index=-1):
    dict_left = index_dict(snmp_results, segment_index)
    dict_reverse = {v: k for k,v in dict_left.items()} 
    return dict_reverse


def render_html(result, template_filename, html_out_filename):
    template_dir = cfg.get('global', 'install_dir') + '/checks'
    template_file = template_dir + '/' + template_filename
    html_dir = cfg.get('global', 'html_dir')
    html_file = html_dir + '/' + html_out_filename
    template_loader = jinja2.FileSystemLoader(searchpath="/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    html = template.render({'result': result})
    f = open(html_file, 'w')
    f.write(html)
    f.close()


def get_neighbor_name(iface_name):
    # regexp to recognize '::' port descriptions
    uplink_rexp_pattern = '.*(::[a-z0-9-]+).*'
    uplink_rexp = re.compile(uplink_rexp_pattern)
    match = uplink_rexp.match(iface_name)
    if match:
        neighbor = match.group(1)
        neighbor = neighbor[2:]
        return neighbor
    else:
        return None
