import asyncio
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

# Server sends the Session ID and asks the user
# to mention the metric that needs to be converted

class RequestDetails(PacketType):
    DEFINITION_IDENTIFIER = "Antara.Packet2"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("metric", STRING)]

# Client sends the data value that needs to be converted

class SendData(PacketType):
    DEFINITION_IDENTIFIER = "Antara.Packet3"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("metricFrom", STRING), ("metricTo", STRING), ("value", UINT32)]

# Server converts the value and prints it out

class Conversion(PacketType):
    DEFINITION_IDENTIFIER = "Antara.Packet4"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("finalvalue", UINT32)]

global pair
pair = {}

# Protcol - Server Class

class MyServer(asyncio.Protocol):

    def __init__(self):
        self._transport = None
        self.SessionID = random.randrange(1, 50, 1)
        pair[self.SessionID] = "Client_Hello"

    def connection_made(self, transport ):
        self._transport = transport
        print ("****** Server Connection made! ******")
        self._deserializer = PacketType.Deserializer()

    def data_received(self, data):
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for packet in self._deserializer.nextPackets():
            if (packet.DEFINITION_IDENTIFIER == "Antara.Packet1" and pair[self.SessionID] == "Client_Hello"):
                Serverpacket1 = RequestDetails()
                Serverpacket1.SessionID = self.SessionID
                Serverpacket1.metric = "C to F"
                Serverbytes1 = Serverpacket1.__serialize__()
                pair[self.SessionID] = "Requesting_Details"
                self._transport.write(Serverbytes1)

            elif (packet.DEFINITION_IDENTIFIER == "Antara.Packet3" and pair[self.SessionID] == "Data_Sent"):
                Serverpacket2 = Conversion()
                Serverpacket2.SessionID = packet.SessionID
                Serverpacket2.finalvalue = packet.value*(9/5) + 32
                print ("Final value is: ",Serverpacket2.finalvalue)

            else:
                print ("No packet :(")
                self._transport.close()

    def connection_lost(self, exc):
        self._transport = None

class MyClient(asyncio.Protocol):

    def __init__(self):
        self._transport = None

    def Initial_Packet(self):
        print ("========================")

    def connection_made(self, transport):
        self._transport = transport
        print("***** Client Connection made! ******")
        InitialPacket = RequestConversion()
        InitialPacketBytes = InitialPacket.__serialize__()
        self._transport.write(InitialPacketBytes)
        self._deserializer = PacketType.Deserializer()

    def data_received(self, data):
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for packet in self._deserializer.nextPackets():
            if (packet.DEFINITION_IDENTIFIER == "Antara.Packet2"):

                ClientPacket2 = SendData()
                ClientPacket2.SessionID = packet.SessionID
                ClientPacket2.metricFrom = "Celsius"
                ClientPacket2.metricTo = "Fahrenheit"
                ClientPacket2.value = self.input_value()
                print ("Value to convert is: ", self.input_metric)
                ClientPacket2bytes = ClientPacket2.__serialize__()
                pair[packet.SessionID] = "Data_Sent"
                self._transport.write(ClientPacket2bytes)

            else:
                print ("No packet")
                self._transport.close()

    def input_value(self):
        self.input_metric = 44
        return self.input_metric

    def connection_lost(self, exc):
        self._transport = None

def UnitTest():

    loop = TestLoopEx()
    asyncio.set_event_loop(loop)

    Server = MyServer()
    Client = MyClient()

    transportToServer = MockTransportToProtocol(myProtocol= Client)
    transportToClient = MockTransportToProtocol(myProtocol= Server)
    transportToServer.setRemoteTransport(transportToClient)
    transportToClient.setRemoteTransport(transportToServer)

    Server.connection_made(transportToClient)
    Client.Initial_Packet()
    Client.connection_made(transportToServer)

if __name__ == '__main__':
    UnitTest()

