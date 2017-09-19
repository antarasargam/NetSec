import asyncio
import playground
import sys
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


# Server sends the Session ID and asks the user
# to mention the metric that needs to be converted

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

global pair_ID_
pair_ID = {}

class passthrough2(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        print("Passthrough 2 connection made \n")
        higherTransport1 = StackingTransport(self.transport)
        self.higherProtocol().connection_made(higherTransport1)

    def data_received(self, data):
        print ("===Pass through 2 data received=== \n")
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.transport = None
        self.higherProtocol().connection_lost(exc)


class passthrough1(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        print ("Pass through 1 connection made \n")
        higherTransport2 = StackingTransport(self.transport)
        self.higherProtocol().connection_made(higherTransport2)

    def data_received(self, data):
        print ("===Pass through 1 data received===")
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.transport = None
        self.higherProtocol().connection_lost(exc)

class MyServer(asyncio.Protocol):

    def __init__(self):
        self.transport = None
        self.deserializer = PacketType.Deserializer()

    def connection_made(self, transport ):
        print ("Server Connection made!")
        self.transport = transport
        self.SessionID = random.randrange(1,50,1)
        pair_ID[self.SessionID] = "Client_Hello"
        print (pair_ID[self.SessionID])

    def data_received(self, data):
        self.deserializer = PacketType.Deserializer()
        self.deserializer.update(data)
        for packet in self.deserializer.nextPackets():
            if isinstance(packet, RequestConversion) and pair_ID[self.SessionID] == "Client_Hello":
                Serverpacket1 = RequestDetails()
                Serverpacket1.SessionID = self.SessionID
                Serverpacket1.metric = "C to F"
                Serverbytes1 = Serverpacket1.__serialize__()
                self.transport.write(Serverbytes1)
                pair_ID[self.SessionID] = "Requesting_Details"

            elif isinstance(packet, SendData) and pair_ID[packet.SessionID] == "Requesting_Details":
                Serverpacket2 = Conversion()
                Serverpacket2.SessionID = packet.SessionID
                Serverpacket2.finalvalue = packet.value*(9/5) + 32
                print (Serverpacket2)
                print ("Final value is: ",Serverpacket2.finalvalue)
                Serverpacket2bytes = Serverpacket2.__serialize__()
                self.transport.write(Serverpacket2bytes)


            else:
                print ("No packet :(")
                self.transport.close()

    def connection_lost(self, exc):
        self.transport = None


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    f = StackingProtocolFactory(lambda: passthrough1(), lambda: passthrough2())
    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("passthrough", ptConnector)
    coro = playground.getConnector('passthrough').create_playground_server(lambda: MyServer(), 101)
    server = loop.run_until_complete(coro)
    print ("Server's coro is done")
    loop.run_forever()
    loop.close()
