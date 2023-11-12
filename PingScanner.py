import os
import sys
import re
import subprocess
import concurrent.futures



def IPFileReader():
	try:
		reader = open(sys.argv[1])
		IPList = reader.readlines()
		reader.close()
		IPList = list(map(str.strip, IPList))
		IPList = [eachIPAddr for eachIPAddr in IPList if eachIPAddr != ""]
		return IPList
	except FileNotFoundError:
		sys.exit("No valid IP list file found.")
	except Exception as e:
		sys.exit(f"Something went wrong in IPFileReader function!: {e}")





def IPListSplitter(IPList, partNumber):
	splittedIPListLists = list()
	listLength = len(IPList)
	partSize = listLength // partNumber

	for part in range(1, partNumber+1):
		if part != (partNumber):
			trimmedList = IPList[(partSize*part)-partSize:(partSize*part)]
		else:
			trimmedList = IPList[(partSize*part)-partSize:]
		splittedIPListLists.append(trimmedList)
	return splittedIPListLists




def DigitExtractor(defaultValue, propertyName):
	result = defaultValue
	try:
		for i in range(2, len(sys.argv)):
			if "--"+propertyName in sys.argv[i]:
				position = sys.argv[i].find('=')
				result = sys.argv[i][(position+1):]
				if result.isdigit() == False:
					result = defaultValue
		return int(result)
	except Exception as e:
		sys.exit(f"Something went wrong in DigitExtractor function!: {e}")





def PacketCountExtractor():
	return DigitExtractor(2, "packetCount")





def ThreadCountExtractor():
	return DigitExtractor(1, "threadCount")





def IPAddrStructureVerifier(IPAddr):
	try:
		regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
		if re.match(regex, IPAddr) == None:
			return False
		else:
			return True
	except Exception as e:
		sys.exit(f"Something went wrong in IPAddrStructureVerifier function!: {e}")





def AvailibleServerFileWriter(IPAddr):
	try:
		availibleServices = open('availibleServices.txt', 'a')
		availibleServices.write(str(IPAddr)+"\n")
		availibleServices.close()
	except Exception as e:
		print(f"Something went wrong in AvailibleServerFileWriter function!: {e}")





def IncorrectIPsFileWriter(IPAddr):
	try:
		# os.mknod('UnestablishableIPs.txt')
		UnestablishableIPs = open('IncorrectIPs.txt', 'a')
		UnestablishableIPs.write(str(IPAddr)+"\n")
		UnestablishableIPs.close()
	except Exception as e:
		print(f"Something went wrong in IncorrectIPsFileWriter function!: {e}")





def ping(ip, packetCount):
	# Returning 0 means that the sever is up.
	return subprocess.call(["ping", "-c", str(packetCount), str(ip)]) == 0





def ServerAvailibilityChecker(IPList, packetCount):
	IPListLength = len(IPList)

	for i in range(IPListLength):
		if IPAddrStructureVerifier(IPList[i]) == True:
			if ping(IPList[i], packetCount) == True:
				AvailibleServerFileWriter(IPList[i])
				print(IPList[i] + " is availible.")
			else:
				print(IPList[i] + " is not availible.")
		else:
			IncorrectIPsFileWriter(IPList[i])
			invalidIPCounter += 1
			print(IPList[i] + " doesn't have the correct structure.")





def main():
	packetCount = PacketCountExtractor()
	threadCount = ThreadCountExtractor()
	IPList = IPFileReader()
	splittedIPListLists = IPListSplitter(IPList, threadCount) # A list which contains splitted lists of IP Addres.


	print("Packet Count: " + str(packetCount) + ".")
	print("Thread Count: " + str(threadCount) + ".")


	pool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
	for i in range(threadCount):
		pool.submit(ServerAvailibilityChecker, splittedIPListLists[i], packetCount)
	pool.shutdown(wait=True)
	print("Scanning Done!")




main()
