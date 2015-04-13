# -*- coding : UTF-8 -*-
from ConfigParser import SafeConfigParser
import os
import re
from datetime import datetime
import sys

from save_to_sqlite3_db import *
from diff.XML.XMLParsing.dhcp_log_parser.packet_object import *


__author__ = 'irymaruk'

parser = SafeConfigParser()
parser.read('config.cfg')
root_folder_path = parser.get('FILES', 'root_folder_path')
file_extension = parser.get('FILES', 'file_extension')
pattern_include = parser.get('PACKETS', 'pattern_include')
pattern_exclude = parser.get('PACKETS', 'pattern_exclude')
recreate_table = parser.getboolean('DB', 'recreate_table')
db_name = parser.get('DB', 'db_name')
save_in_xml = parser.getboolean('DB', 'save_in_xml')
save_out_xml = parser.getboolean('DB', 'save_out_xml')

# if root_folder_path
if not root_folder_path:
    root_folder_path = os.path.dirname(os.path.abspath(__file__))
    print 'root_folder_path = current directory'

# split and then strip white spaces
if pattern_include:
    pattern_include = [x.strip() for x in pattern_include.split(',')]
if pattern_exclude:
    pattern_exclude = [x.strip() for x in pattern_exclude.split(',')]
print 'pattern_include =', pattern_include
print 'pattern_exclude =', pattern_exclude


def create_list_of_files_recursive():
    local_list_files = []
    for directory, dir_names, file_names in os.walk(root_folder_path):
        for filename in file_names:
            if re.search(file_extension + '$', filename):
                local_list_files.append(directory + '\\' + filename)
    return local_list_files


def packet_check_for_save(packet_all_lines):
    packets_counter['all'] += 1
    if pattern_exclude:
        if [i for i in pattern_exclude if i in str(packet_all_lines)]:
            packets_counter['skipped'] += 1
            return # do nothing with packet
    if pattern_include:
        if 'ALL_PACKETS' in pattern_include or [i for i in pattern_include if i in str(packet_all_lines)]:
            packet = Packet(packet_all_lines)
            data_source.save_dhcp_packet(packet, save_in_xml, save_out_xml)
            packets_counter['matched'] += 1
    return

def split_to_packets(file_name):
    packet_all_lines = []
    with open(file_name, 'rb') as file_in:
        for line in file_in:
            if line.startswith("#7"):
                packet_check_for_save(packet_all_lines)
            if line.startswith("#1"):
                packet_all_lines = []
                packet_all_lines.append(line)
            else:
                packet_all_lines.append(line)


#####################     BEGIN PROGRAM     #####################

# scanning folder for log files
if os.path.exists(root_folder_path):
    list_files = create_list_of_files_recursive()
else:
    print 'Not existing path:', root_folder_path
    sys.exit()
print '\n   Files for parsing:'
for file_name in list_files:
    print file_name

now_time1 = datetime.now()
print '\n   start time:', str(now_time1)
try:
    data_source = Db(db_name, recreate_table)
    packets_counter_summ = {'all': 0, 'matched': 0, 'skipped': 0}
    for file_name in list_files:
        packets_counter = {'all': 0, 'matched': 0, 'skipped': 0}
        print 'parsing ', file_name
        split_to_packets(file_name)
        print packets_counter
        for k,v in packets_counter.items():
            packets_counter_summ[k] += v
        data_source.commit()
except sqlite3.Error, e:
            print "Error with DB: %s" % e.args[0]
            raise
finally:
    if data_source:
        data_source.commit()
        data_source.conn.close()

now_time2 = datetime.now()
print '\n           SUMMARY:'
print packets_counter_summ
print '\n STAT: ', str(now_time1), 'FINISH: ', str(now_time2)
diff = now_time2 - now_time1
print('DIFF: ', str(diff))


