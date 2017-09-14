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

class MyServer(asyncio.Protocol):

    def __init__(self):
        self._transport = None
        #self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport ):
        self._transport = transport
        print ("Server Connection made!")
        self.SessionID = random.randrange(1,50,1)
        #pair[self.SessionID] = "Client_Hello"

    def data_received(self, data):
        print ("Hi???")
        print (data)
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for packet in self._deserializer.nextPackets():
            if (packet.DEFINITION_IDENTIFIER == "Antara.Packet1"):
                Serverpacket1 = RequestDetails()
                Serverpacket1.SessionID = self.SessionID
                Serverpacket1.metric = "C to F"
                Serverbytes1 = Serverpacket1.__serialize__()
                #pair[self.SessionID] = "Requesting_Details"
                self._transport.write(Serverbytes1)
            elif (packet.DEFINITION_IDENTIFIER == "Antara.Packet3"):
                print ("Enters packet2")
                Serverpacket2 = Conversion()
                Serverpacket2.SessionID = packet.SessionID
                Serverpacket2.finalvalue = packet.value*(9/5) + 32
                print (Serverpacket2)
                print ("Final value is: ",Serverpacket2.finalvalue)
                Serverpacket2bytes = Serverpacket2.__serialize__()
                self._transport.write(Serverpacket2bytes)

            else:
                print ("No packet :(")
                self._transport.close()

    def connection_lost(self, exc):
        self._transport = None


loop = asyncio.get_event_loop()
playground.getConnector().create_playground_server(MyServer, 101)

#server = loop.run_until_complete(coro)
print ('Serving on socket: ')

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass


#server.close()
#loop.run_until_complete(server.wait_closed())
loop.close()
