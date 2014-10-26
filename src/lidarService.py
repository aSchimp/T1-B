#### See the following page for details on the LIDAR unit packet structure: http://xv11hacking.wikispaces.com/LIDAR+Sensor#toc4 ####

import serial
import threading

class LidarPacket(object):
	def __init__(self, index, speed, dist1, dist2, dist3, dist4):
		self.index = index
		self.speed = speed
		self.dist1 = dist1
		self.dist2 = dist2
		self.dist3 = dist3
		self.dist4 = dist4

def lidarChecksum(data):
    """Compute and return the checksum as an int."""
    # group the data by word, little-endian
    data_list = []
    for t in range(10):
        data_list.append( data[2*t] + (data[2*t+1]<<8) )
 
    # compute the checksum on 32 bits
    chk32 = 0
    for d in data_list:
        chk32 = (chk32 << 1) + d
 
    # return a value wrapped around on 15bits, and truncated to still fit into 15 bits
    checksum = (chk32 & 0x7FFF) + ( chk32 >> 15 ) # wrap around to fit into 15 bits
    checksum = checksum & 0x7FFF # truncate to 15 bits
    return int( checksum )

# return value of -1 means data is invalid
def parsePacketDataSection(bytes):
	# if the 8th bit of the byte 1 is set, the data is invalid; the 7th bit of byte 1 is a strength warning (varies with material sometimes) flag, but we are ignoring it for now
	if bytes[1] & 128 == 128:
		return -1

	# get distance from byte 0 and byte 1; byte 2 and byte 3 contain signal strength data, which we are ignoring for now
	return int(bytes[0] + ((bytes[1] & 63) << 8)

def parsePacket(bytes):
	# first byte in packet must be 0xFA
	if (bytes[0] != 0xFA):
		return None

	# verify data via checksum
	if lidarChecksum(butes[0:20]) != int(bytes[20] + (bytes[21] << 8)):
		# invalid data
		return None

	# packet index must be between 0xA0 and 0xF9
	index = bytes[1]
	if (index < 0xA0 or index > 0xF9):
		return None;

	# adjust index to 0 based index
	index = index - 0xA0

	# speed unit used by the LIDAR in 64ths of an RPM; we want the speed in RPMs
	speed = int(bytes[2] + (bytes[3]<<8))/64.0

	distances = []
	for x in range(1,5):
		distances.append(parsePacketDataSection(bytes[4*x:4*x+4]))

	return LidarPacket(index, speed, distances[0], distances[1], distances[2], distances[3])

def updateMap(mapData, packets):
	mapDataLock.aquire()
	try:
		mapData[:] = [-1] * len(mapData) # clear map data
		for packet in packets:
			mapData[packet.index] = packet.dist1
			mapData[packet.index + 1] = packet.dist2
			mapData[packet.index + 2] = packet.dist3
			mapData[packet.index + 3] = packet.dist4
	finally:
		mapDataLock.release()

def readLidar(mapData, rpmData):
	ser = serial.Serial('/dev/ttyO2', 115200, timeout=1)
	ser.flushInput()
	ser.flushOutput()
	packetBuffer = []
	currentPacketData = []
	while True:
		bytesToRead = ser.inWaiting()
		bytes = ser.read(bytesToRead)
		for b in bytes:
			# if we're starting a new packet, but the current byte doesn't mark the beginning of the packet, skip it
			if (len(currentPacketData) == 0 && b != 0xFA):
				continue;
			currentPacketData.append(b)
			if len(currentPacketData) == 22:
				packet = parsePacket(currentPacketData)
				if packet is None:
					# packet was invalid; check for 0xFA packet start marker in the last packet, as sometimes some bytes are dropped and the next packet is already started
					try:
						nextIndex = currentPacketData[1:].index(0xFA) + 1
						currentPacketData = currentPacketData[nextIndex:]
					except ValueError:
						currentPacketData = []
				else:
					# update rpmData, but only keep 8 revolutions of data (90 rpm readings per revolution)
					rpmDataLock.aquire()
					try:
						rpmData.insert(0, packet.speed)
						if (len(rpmData) == 721):
							del rpmData[720]
					finally:
						rpmDataLock.release()

					# update map if necessary, or buffer the packet until the revolution completes
					packetBuffer.append(packet)
					if (packet.index == 89):
						updateMap(mapData)

					# reset currentPacketData
					currentPacketData = []


def manageLidarMotor(rpmData):
	# maintain lidar motor rpms here at about 275 rpm (docs say it should be between 180 and 349); may need to experiment with different values; if too high, packets will start dropping; if too low, the firmware on the LIDAR sends nothing



mapDataLock = threading.Lock()
mapData = [-1] * 360;
rpmDataLock = threading.Lock()
rpmData = [];

lidarReaderThread = threading.Thread(target = readLidar, args = (mapData, rpmData))
lidarMotorThread = threading.Thread(target = manageLidarMotor, args = (rpmData))