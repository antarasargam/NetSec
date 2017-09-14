import asyncio
import playground
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, BUFFER, STRING
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol
import random

#from playground.common import logging as p_logging
#p_logging.EnablePresetLogging(p_logging.PRESET_TEST)

# Client Requesting for Conversion

class RequestConversion(PacketType):
    DEFINITION_IDENTIFIER = "Antara.Packet1"
    DEFINITION_VERSION = "1.0"

# Client sends the data value that needs to be converted

class SendData(PacketType):
    DEFINITION_IDENTIFIER = "Antara.Packet3"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("metricFrom", STRING), ("metricTo", STRING), ("value", UINT32)]

class RequestDetails(PacketType):
    DEFINITION_IDENTIFIER = "Antara.Packet2"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("metric", STRING)]

# Server converts the value and prints it out

class Conversion(PacketType):
    DEFINITION_IDENTIFIER = "Antara.Packet4"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("finalvalue", UINT32)]


class MyClient(asyncio.Protocol):

    def __init__(self, loop, message):
        self.loop = loop
        self._transport = None
        self.message = message

    def connection_made(self, transport):
        self._transport = transport
        print("Client Connection made!")
        self.message = message.__serialize__()
        print (self.message)
        self._transport.write(self.message)
        self._deserializer = PacketType.Deserializer()

    def data_received(self, data):
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for packet in self._deserializer.nextPackets():
            print (packet)
            if (packet.DEFINITION_IDENTIFIER == "Antara.Packet2"):

                ClientPacket2 = SendData()
                ClientPacket2.SessionID = packet.SessionID
                ClientPacket2.metricFrom = "Celsius"
                ClientPacket2.metricTo = "Fahrenheit"
                ClientPacket2.value = self.input_value()
                ClientPacket2bytes = ClientPacket2.__serialize__()
                #pair[packet.SessionID] = "Data_Sent"
                self._transport.write(ClientPacket2bytes)
                print("Found packet - 1 from server!")

            elif (isinstance(packet, Conversion)):
                print ("The final value received is: ",packet.finalvalue)

            else:
                print ("No packet")
                self._transport.close()

    def input_value(self):
        self.input_metric = input ("What value to convert: ")
        return self.input_metric

    def connection_lost(self, exc):
        self._transport = None

loop = asyncio.get_event_loop()

message = RequestConversion()
playground.getConnector().create_playground_connection(lambda: MyClient(loop,message), '20174.1.1.2', 101)

#loop.run_until_complete()
loop.run_forever()

loop.close()
