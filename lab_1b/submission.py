"""Below is a basic metric conversion protocol for converting Celsius to Fahrenheit
   I haven't incorporated other metric conversions in order to keep this
   assignment simple. Will be adding other metrics for the next lab."""



from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, BUFFER, STRING

"""Client Requesting for Conversion"""

class RequestConversion(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.Antara.Packet1"
    DEFINITION_VERSION = "1.0"

"""Server sends the Session ID and asks the user to mention the metric that needs to be converted"""

class RequestDetails(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.Antara.Packet2"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("metric", STRING)]

"""Client sends the data value that needs to be converted"""

class SendData(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.Antara.Packet3"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("metricFrom", STRING), ("metricTo", STRING), ("value", UINT32)]

"""Server converts the value and prints it out"""

class Conversion(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.Antara.Packet4"
    DEFINITION_VERSION = "1.0"

    FIELDS = [("SessionID", UINT32), ("finalvalue", UINT32)]

""" Unit test """

def BasicCtoFTest1():

    """Basic Unit Test"""
    """First packet"""
    packet1 = RequestConversion()
    packet1Bytes = packet1.__serialize__()
    packet1a = RequestConversion.Deserialize(packet1Bytes)
    assert packet1 == packet1a

    """Second Packet"""
    packet2 = RequestDetails()
    packet2.SessionID = 1
    packet2.metric = "Celsius to Fahrenheit"
    packet2Bytes = packet2.__serialize__()
    packet2a = RequestDetails.Deserialize(packet2Bytes)
    assert packet2 == packet2a

    """Third packet"""
    packet3 = SendData()
    packet3.SessionID = 1
    packet3.metricFrom = "Celsius"
    packet3.metricTo = "Fahrenheit"
    packet3.value = input("What's the value you want to convert (Celsius to Fahrenheit): ")
    packet3Bytes = packet3.__serialize__()
    packet3a = SendData.Deserialize(packet3Bytes)
    assert packet3 == packet3a

    """Fourth packet"""
    packet4 = Conversion()
    packet4.SessionID = 1
    packet4.finalvalue = packet3.value*(9/5) + 32

    packet4Bytes = packet4.__serialize__()
    packet4a = Conversion.Deserialize(packet4Bytes)
    assert packet4 == packet4a

    print ("******Deserializer*******")
    deserializer = Conversion.Deserializer()
    print ("Data of {} bytes".format(len(packet4Bytes)))

    while len(packet4Bytes) > 0:
        chunks, packet4Bytes = packet4Bytes[:5], packet4Bytes[5:]
        deserializer.update(chunks)

        for packet in deserializer.nextPackets():
            print ("The Final converted value is : ",packet.finalvalue, "F")


if __name__=="__main__":
    BasicCtoFTest1()
