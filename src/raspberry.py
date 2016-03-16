#!/usr/bin/env python

#
# 433MHz receiver.
#
GROUP_ID = 1

import time
from pi_switch import RCSwitchReceiver

receiver = RCSwitchReceiver()
receiver.enableReceive(2)

def receive_if_available():
    if not receiver.available():
        return

    packet = receiver.getReceivedValue()
    receiver.resetAvailable()

    if packet and check_group(packet):
        return decode(packet)

def check_group(packet):
    return (packet >> 24) == GROUP_ID

def decode(packet):
    sid = (packet >> 16) & 0xff
    data = packet & 0xffff
    if data & 0x8000:
        data = data - 0x10000
    return sid, data

#
# MQTT client.
#
import ibmiotf.device

def connect(config):
    options = ibmiotf.device.ParseConfigFile(config)
    client = ibmiotf.device.Client(options)
    client.connect()
    client.commandCallback = on_message

client = connect('device.cfg')

def on_message(cmd):
    if cmd.command != 'button':
        return

    print cmd

sid_to_topic = ['temperature', 'angle']

def send_data(sid, data):
    topic = sid_to_topic[sid]
    client.publishEvent(topic, 'json', data)

def main():
    while True:
        payload = receive_if_available()
        if payload:
            sid, data = payload
            if not 0 <= sid <= 1:
                print sid, data, payload
            send_data(sid, data)
        else:
            time.sleep(0.1)

if __name__ == '__main__':
    main()
