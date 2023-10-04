from socket import socket, AF_INET, SOCK_DGRAM
import struct
from datetime import datetime

def getNTPTimeValue(server="time.apple.com", port=123) -> (bytes, float, float):
    # make an NTP packet
    NTP_pkt = bytearray(48)
    NTP_pkt[0] = 0x1B

    # take a timestamp
    timestamp_1 = datetime.utcnow()
    sec_1 = timestamp_1.day*24.0*60.0*60.0 + timestamp_1.second
    T1 = sec_1 + float(timestamp_1.microsecond / 1000000.0)

    # send packet to the server,port address
    client = socket(AF_INET, SOCK_DGRAM)
    client.sendto(NTP_pkt, (server, port))

    # receive the response packet
    pkt, serverAddress = client.recvfrom(1024)

    # take a timestamp
    timestamp_2 = datetime.utcnow()
    sec_2 = timestamp_2.day*24.0*60.0*60.0 + timestamp_2.second
    T4 = sec_2 + float(timestamp_2.microsecond / 1000000.0)

    # close client
    client.close()

    # return a 3-tuple:
    return (pkt, T1, T4)

def ntpPktToRTTandOffset(pkt: bytes, T1: float, T4: float) -> (float, float):
    # declare constant
    EPOCH = 2208988800

    # unpack the pkt
    unpackedData = struct.unpack('!12I', pkt)

    # get bytes for seconds and fractions for T2 and T3
    T2_seconds = unpackedData[8]
    T2_fraction = unpackedData[9]
    T3_seconds = unpackedData[10]
    T3_fraction = unpackedData[11]

    # combine the seconds and fraction into 1 number for T2 and T3
    T2 = T2_seconds + T2_fraction / pow(2,32) - EPOCH
    T3 = T3_seconds + T3_fraction / pow(2,32) - EPOCH

    # compute RTT and offset
    RTT =  (T4 - T1) - (T3 - T2)
    offset = ((T2 - T1) + (T3 - T4)) / 2

    # return RTT and offset
    return (RTT, offset)

def getCurrentTime(server="time.apple.com", port=123, iters=20) -> float:

    offsets = []
    for _ in range(iters):
        pkt, T1, T4 = getNTPTimeValue(server, port)
        RTT, offset = ntpPktToRTTandOffset(pkt, T1, T4)
        offsets.append(offset)

    # compute average offset
    avg_offset = sum(offsets) / len(offsets)

    # add average offset to currentTime
    curr = datetime.utcnow()
    sec = curr.day*24.0*60.0*60.0 + curr.second
    currentTime = sec + float(curr.microsecond / 1000000.0)
    currentTime = currentTime + avg_offset

    return currentTime

if __name__ == "__main__":
    print(getCurrentTime())
