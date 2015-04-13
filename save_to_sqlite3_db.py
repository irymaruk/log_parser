# -*- coding : UTF-8 -*-
from os import path, remove
import sqlite3


class Db():
    def __init__(self, db_name="data.db", recreate_table=False):
        try:
            self.conn = sqlite3.connect(db_name)
            self.conn.text_factory = str
            self.curr = self.conn.cursor()
            self._recreate_table(recreate_table)
        except sqlite3.Error, e:
            print "Error connecting to DB: %s" % e.args[0]
            raise

    def _recreate_table(self, recreate_table):
        if recreate_table:
            self.curr.execute("DROP TABLE IF EXISTS DHCP_LOG")
        self.curr.execute("CREATE TABLE IF NOT EXISTS DHCP_LOG(DATE_IN TEXT, TIME_PROC INTEGER, PACKET_TYPE_IN INTEGER, PACKET_REQ_TYPE INTEGER, PACKET_TYPE_OUT INTEGER, PACKET_ID INTEGER, RELAY_IP TEXT, SERVER_IP TEXT, MSG TEXT, XML_IN TEXT, XML_OUT TEXT)")
        # self.conn.commit()

    def save_dhcp_packet(self, packet, save_in_xml=True, save_out_xml=True):
        insert_sql = "INSERT INTO DHCP_LOG(DATE_IN, TIME_PROC, PACKET_TYPE_IN, PACKET_REQ_TYPE, PACKET_TYPE_OUT, PACKET_ID, RELAY_IP, SERVER_IP, MSG, XML_IN, XML_OUT) \
values (:DATE_IN, :TIME_PROC, :PACKET_TYPE_IN, :PACKET_REQ_TYPE, :PACKET_TYPE_OUT, :PACKET_ID, :RELAY_IP, :SERVER_IP, :MSG, :XML_IN, :XML_OUT)"
        try:
            self.curr.execute(insert_sql, {'DATE_IN': packet.packet_in_date,
                                           'TIME_PROC': packet.packet_time_process,
                                           'PACKET_TYPE_IN': packet.packet_type_in,
                                           'PACKET_REQ_TYPE': packet.packet_request_sub_type,
                                           'PACKET_TYPE_OUT': packet.packet_type_out,
                                           'PACKET_ID': packet.packet_id,
                                           'RELAY_IP': packet.packet_relay_ip,
                                           'SERVER_IP': packet.packet_srv_ip,
                                           'MSG': packet.packet_mesg,
                                           'XML_IN': packet.packet_xml_in if save_in_xml else None,
                                           'XML_OUT': packet.packet_xml_out if save_out_xml else None})
            # self.conn.commit()
        except sqlite3.Error, e:
            self.conn.rollback()
            print "Rollback performed while inserting PACKET_ID =", packet._get_packet_id()
            print "Error %s:" % e.args[0]
            raise

    # @staticmethod
    def commit(self):
        self.conn.commit()