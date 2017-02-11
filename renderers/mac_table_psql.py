import sys
import os
import re
import datetime
import jinja2
import pprint
sys.path.insert(0, "..")
import config as cfg
import ago
from datetime import timedelta
import psycopg2


def atoi(text):
    return int(text) if text.isdigit() else text


def render_template(result, template_filename):
    template_loader = jinja2.FileSystemLoader(searchpath="/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_filename)
    datetime
    rendered = template.render({'result': result, 'date': datetime.datetime.now().isoformat()})
    return rendered


def render_and_write_template(result, template_filename, output_filename):
    rendered = render_template(result, template_filename)
    write_file(output_filename)


def write_file(text, filename):
    output_file = open(filename, 'w')
    output_file.write(text)
    output_file.close()

template_dir = cfg.get('global', 'install_dir') + '/renderers/'


def run(world):
    conn = None
    try:
        conn = psycopg2.connect("dbname='TODO' user='GET' password='THIS FROM CONFIG' host='127.0.0.1'")
    except Exception as e:
        print("I am unable to connect to the database.")
        print(e)
    cur = conn.cursor()

    for dev_name, dev in world.items():
        for entry in dev['mac_table']:
            ifIndex = int(entry['ifIndex'])
            ifName = dev['ifaces'][ifIndex]['name']
            vlan = int(entry['vlan'])
            #print("""UPDATE mactable set count = count + 1 where mac = %s and portname = %s and device = %s and vlan = %s;""" % (entry['mac'], ifName, dev_name, vlan))
            cur.execute("""UPDATE mactable set count = count + 1 where mac = %s and portname = %s and device = %s and vlan = %s;""", (entry['mac'], ifName, dev_name, vlan))
            update_result = cur.rowcount
            print("update returned", update_result)
            conn.commit()
            if update_result == 0:
                try:
                    print('inserting')
                    cur.execute("""INSERT INTO mactable (mac, portname, device, vlan) values (%s, %s, %s, %s);""", (entry['mac'], ifName, dev_name, vlan))
                    conn.commit()
                except psycopg2.IntegrityError as ie:
                    if ie.pgcode == '23505':  # UNIQUE constraint violation, this ip-mac pair already exists in the table
                        print('resetting')
                        conn.reset()
                        conn.commit()
                    else:
                        raise ie
                except Exception as e:
                    print("I can't INSERT")
                    print(type(e))
                    print(e.pgcode)
                    raise e
    cur.close()
    conn.close()
