#!/usr/bin/env python3

############################################################################
#                                                                          #
#  PyTCP - Python TCP/IP stack                                             #
#  Copyright (C) 2020  Sebastian Majewski                                  #
#                                                                          #
#  This program is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or       #
#  (at your option) any later version.                                     #
#                                                                          #
#  This program is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#  GNU General Public License for more details.                            #
#                                                                          #
#  You should have received a copy of the GNU General Public License       #
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                          #
#  Author's email: ccie18643@gmail.com                                     #
#  Github repository: https://github.com/ccie18643/PyTCP                   #
#                                                                          #
############################################################################

##############################################################################################
#                                                                                            #
#  This program is a work in progress and it changes on daily basis due to new features      #
#  being implemented, changes being made to already implemented features, bug fixes, etc.    #
#  Therefore if the current version is not working as expected try to clone it again the     #
#  next day or shoot me an email describing the problem. Any input is appreciated. Also      #
#  keep in mind that some features may be implemented only partially (as needed for stack    #
#  operation) or they may be implemented in sub-optimal or not 100% RFC compliant way (due   #
#  to lack of time) or last but not least they may contain bug(s) that i didn't notice yet.  #
#                                                                                            #
##############################################################################################


#
# service_udp_echo.py - 'user space' service UDP Echo (RFC 862)
#


import threading

import udp_socket
from malpi import malpa, malpka
from tracker import Tracker
from udp_metadata import UdpMetadata


class ServiceUdpEcho:
    """ UDP Echo service support class """

    def __init__(self, local_ip_address="*", local_port=7):
        """ Class constructor """

        threading.Thread(target=self.__thread_service, args=(local_ip_address, local_port)).start()

    @staticmethod
    def __thread_service(local_ip_address, local_port):
        """ Service initialization and rx/tx loop """

        socket = udp_socket.UdpSocket()
        socket.bind(local_ip_address, local_port)
        print(f"Service UDP Echo: Socket created, bound to {local_ip_address}, port {local_port}")

        while True:
            packet_rx = socket.receive_from()
            message = packet_rx.raw_data
            print(f"Service UDP Echo: Received {len(message)} bytes from {packet_rx.remote_ip_address}, port {packet_rx.remote_port}")

            if "malpka" in str(message, "utf-8").strip().lower():
                message = bytes(malpka, "utf-8")

            elif "malpa" in str(message, "utf-8").strip().lower():
                message = bytes(malpa, "utf-8")

            elif "malpi" in str(message, "utf-8").strip().lower():
                message = b""
                for malpka_line, malpa_line in zip(malpka.split("\n"), malpa.split("\n")):
                    message += bytes(malpka_line + malpa_line + "\n", "utf-8")

            packet_tx = UdpMetadata(
                local_ip_address=packet_rx.local_ip_address,
                local_port=packet_rx.local_port,
                remote_ip_address=packet_rx.remote_ip_address,
                remote_port=packet_rx.remote_port,
                raw_data=message,
                tracker=Tracker("TX", echo_tracker=packet_rx.tracker),
            )
            socket.send_to(packet_tx)
            print(f"Service UDP Echo: Echo'ed {len(message)} bytes back to {packet_tx.remote_ip_address}, port {packet_tx.remote_port}")
