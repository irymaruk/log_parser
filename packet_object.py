# -*- coding: utf-8 -*-

class PacketTypes():
    def __init__(self):
        pass
    DISCOVER = 1
    OFFER = 2
    REQUEST = 3
    DECLINE = 4
    ACK = 5
    NAK = 6
    RELEASE = 7
    INFORM = 8
    OTHER = 0


class Packet():
    def __init__(self, packet_all_lines):
        self.b1 = []
        self.b2 = []
        self.b3 = []
        self.b4 = []
        self.b5 = []
        self.b6 = []
        self.b7 = []
        self.packet_all_lines = packet_all_lines
        self._split_to_blocks()
        # self.packet_type = PacketTypes.OTHER
        self.packet_id = self._get_packet_id()
        self.packet_in_date = self._get_packet_in_date()
        self.packet_time_process = self._get_packet_time_process()
        self.packet_relay_ip = self._get_packet_relay_ip()
        self.packet_srv_ip = self._get_packet_srv_ip()
        self.packet_mesg = self._get_packet_mesg()
        self.packet_type_in = self._get_packet_type_in()
        self.packet_type_out = self._get_packet_type_out()
        self.packet_xml_in = self._get_packet_xml_in()
        self.packet_xml_out = self._get_packet_xml_out()
        self.packet_request_sub_type = self._get_packet_request_sub_type()

    def _split_to_blocks(self):
        b3_started = False
        b6_started = False
        for line in self.packet_all_lines:
            if line.startswith('#1'):
                self.b1.append(line[2:])
            elif line.startswith('#2'):
                self.b2.append(line[2:])
            elif line.startswith('#3'):
                self.b3.append(line[2:])
                b3_started = True
            elif line.startswith('#4'):
                b3_started = False
                self.b4.append(line[2:])
            elif line.startswith('#5'):
                self.b5.append(line[2:])
            elif line.startswith('#6'):
                self.b3.append(line[2:])
                b6_started = True
            elif line.startswith('#7'):
                b6_started = False
                self.b7.append(line[2:])
            elif b3_started:
                self.b3.append(line)
            elif b6_started:
                self.b6.append(line)

    def _get_packet_id(self):
        return int(''.join(self.b2).split()[-1].strip())

    def _get_packet_in_date(self):
        return (''.join(self.b1).split(" | ")[0].strip())[3:26]

    def _get_packet_time_process(self):
        return ''.join(self.b1).split(" | ")[1].strip()

    def _get_packet_relay_ip(self):
        return ''.join(self.b1).split(" | ")[2].strip()

    def _get_packet_srv_ip(self):
        return ''.join(self.b1).split(" | ")[3].strip()

    def _get_packet_mesg(self):
        return ''.join(self.b1).split(" | ")[4].strip()

    def _get_packet_type_in(self):
        packet_type = ''.join(self.b2).split(" | ")[1].split('=')[-1].strip()
        if packet_type.isdigit():
            return int(packet_type)
        else:
            return None

    def _get_packet_type_out(self):
        packet_type = ''.join(self.b5).split(" | ")[1].split('=')[-1].strip()
        if packet_type.isdigit():
            return int(packet_type)
        else:
            return None

    def _get_packet_xml_in(self):
        return ''.join(self.b3)

    def _get_packet_xml_out(self):
        return ''.join(self.b6)

    def print_packet(self):
        print self.__dict__
        print ''.join(self.packet_all_lines)

    def write_packet(self, file_out):
        file_out.write(''.join(self.packet_all_lines) + '\n')

# DHCP-REQUEST Types
# 1. Selecting:
#    Server-Id = <Serv_IP_addr>, ciaddr = 0, Requested_IpAddr = <Client_IP_addr> (Из поля "yiaddr" предшествующего OFFER пакета)
# 2. Reboot:
#    Server-Id = 0, ciaddr = 0, Requested_IpAddr = <Client_IP_addr> (ранее использовавшийся клиентом адрес)
# 3. Renew:
#    Server-Id = 0, Requested_IpAddr = 0, ciaddr = <Client_IP_addr> (используемый клиентом адрес)
#    передается в режиме unicast
# 4. Rebinding:
#    Server-Id = 0, Requested_IpAddr = 0, ciaddr = <Client_IP_addr> (используемый клиентом адрес)
#    передается в режиме broadcast
#
# http://tools.ietf.org/html/rfc2131#page-22
#    X         |    Server-Id         |      ciaddr        |    Requested_IpAddr    |   bp_broadcast
#--------------|----------------------|--------------------|------------------------|----------------
# Selecting    |     <Serv_IP_addr>   |     0.0.0.0        |     <Client_IP_addr>   |
# Reboot       |      null            |     0.0.0.0        |     <Client_IP_addr>   |
# Renew        |      null            |   <Client_IP_addr> |        null            |        0
# Rebinding    |      null            |   <Client_IP_addr> |        null            |        1


    def _get_packet_request_sub_type(self):
        if self.packet_type_in == PacketTypes.REQUEST:
            if '<Server_Id>' in str(self.b3):
                return 1
            elif '<Requested_Ipaddr>' in str(self.b3):
                return 2
            elif '<bp_broadcast>0</bp_broadcast>' in str(self.b3):
                return 3
            elif '<bp_broadcast>4</bp_broadcast>' in str(self.b3):
                return 4
        else:
            return None
