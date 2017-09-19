import asyncio
import sys
import playground
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, BUFFER, STRING
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol
import random

from playground.network.common import StackingProtocol
from playground.network.common import StackingTransport
from playground.network.common import StackingProtocolFactory

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

global pair_ID
pair_ID = {}

class passthrough1(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        print("Pass through 1 - connection made")
        self.transport = transport
        higherTransport1 = StackingTransport(self.transport)
        self.higherProtocol().connection_made(higherTransport1)

    def data_received(self, data):
        print("Pass through 1 - data received")
        self.higherProtocol().data_received(data)
        print("Pass through 1 - data sent")

    def connection_lost(self, exc):
        print("Pass through 1 connection lost")
        self.transport = None
        self.higherProtocol().connection_lost(exc)


class passthrough2(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        print("Pass through 2 - connection made")
        self.transport = transport
        higherTransport = StackingTransport(self.transport)
        self.higherProtocol().connection_made(higherTransport)

    def data_received(self, data):
        print("Pass through 2 - data received")
        self.higherProtocol().data_received(data)
        print("Pass through 2 - data sent")

    def connection_lost(self, exc):
        print("Pass through 2 connection lost")
        self.transport = None
        self.higherProtocol().connection_lost(exc)

class LoggingStackingTransport(StackingTransport):
    def write(self, data):
        print ("Write got {} bytes of data to pass".format(len(data)))
        super.write(data)

class MyClient(asyncio.Protocol):

    def __init__(self, callback = None):
        self.buffer = ""
        if callback:
            self.callback = callback
            #print("It's in callback_1")
        else:
            self.callback = print

        self.transport = None
        self.deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        print("Client Connection made!")
        self.transport = transport
        self.deserializer = PacketType.Deserializer()

    def data_received(self, data):
        print ("calling data_received")
        self.deserializer = PacketType.Deserializer()
        self.deserializer.update(data)

        #ClientPacket2.SessionID = 0
        pair_ID[0] = "Client_Request"

        for packet in self.deserializer.nextPackets():

            if isinstance(packet, RequestDetails) and pair_ID[0] == "Client_Request":
                ClientPacket2 = SendData()
                ClientPacket2.SessionID = packet.SessionID
                ClientPacket2.metricFrom = "Celsius"
                ClientPacket2.metricTo = "Fahrenheit"
                ClientPacket2.value = self.input_value()
                ClientPacket2bytes = ClientPacket2.__serialize__()
                pair_ID[packet.SessionID] = "Data_Sent"
                self.transport.write(ClientPacket2bytes)

            elif isinstance(packet, Conversion) and pair_ID[packet.SessionID] == "Data_Sent":
                print ("========== The final value received is: ",packet.finalvalue)

            else:
                #print ("No packet")
                self.transport.close()


    def input_value(self):
        self.input_metric = input ("======== What value to convert: ")
        return self.input_metric

    def send(self):
        print ("Packet Sent")
        packet = RequestConversion()
        self.transport.write(packet.__serialize__())

    def connection_lost(self, exc):
        self.transport = None

class ControlProtocol:
    def __init__(self):
        self.txProtocol = None

    def buildProtocol(self):
        return MyClient(self.callback)

    def connect(self, txProtocol):
        self.txProtocol = txProtocol
        print("Connection to Server established")
        self.txProtocol = txProtocol
        self.txProtocol.send()

    def callback(self):
        sys.stdout.flush()



if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    f = StackingProtocolFactory(lambda: passthrough1(), lambda: passthrough2())
    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("passthrough", ptConnector)
    control = ControlProtocol()
    coro = playground.getConnector('passthrough').create_playground_connection(control.buildProtocol, '20174.1.1.1', 101)
    transport, protocol = loop.run_until_complete(coro)
    control.connect(protocol)
    loop.run_forever()
    loop.close()
