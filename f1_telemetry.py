import socket
import struct
import sys
import json
import csv

from operator import itemgetter, attrgetter
import time
from time import gmtime
from time import strftime

#####################################################
# Parameters

IP = "127.0.0.1";	# Change IP if needed
UDP_PORT = 20777;	# Default port for F1 2018

createJsonFile = True;
createCSVFile = False;

createStaticFileName = True;

#####################################################

#Header Packet Stuff
headerString = '<HBBQfBB';

#Laptime Data Struct Stuff
laptimeDataString = '<ffffffffBBBBBBBBB';
laptimeData = [[None] * 17 for i in range(20)];
laptimeList = {
	0: "Last Lap Time",
	1: "Current Lap Time",
	2: "Best Lap Time",
	3: "Sector 1 Time",
	4: "Sector 2 Time",
	5: "Lap Distance",
	6: "Total Distance",
	7: "Car Safety Data",
	8: "Car Position",
	9: "Current Lap Number",
	10: "Pit Status",
	11: "Sector",
	12: "Current Lap Invalid",
	13: "Penalties",
	14: "Grid Position",
	15: "Driver Status",
	16: "Result Status"
}

#Session Data Stuff
sessionDataString = '<BbbB';
sessionData = [None] * 4;

#Participant Data Stuff
participantData = [[None] * 6 for i in range(20)];
participantDataString = '<BBBBB48s';
participantList = {
	0: "Is AI Controlled?",
	1: "Driver ID",
	2: "Team ID",
	3: "Car Number",
	4: "Nationality",
	5: "Name"
}

#Event Data Stuff
eventDataString = '<4s';

#Misc Stuff
lapNumber = [0] * 20;		#	Iterator array for laptime
prevPitStatus = [0] * 20;	#	Stores the previous pitstop status
numOfParticipants = 0;		#	The total players in the game
#laptime = 0;

####################################################

#Final Storage Variables
f_driverNames = [None] * 20;#	Stores the names of the drivers
f_totalLaptimes = [0] * 20;	#	Stores the total lap time of all drivers
f_bestLaptimes = [0] * 20; 	#	Stores the best lap time of all drivers
f_lastLaptimes = [0] * 20; 	#	Stores the last lap time of all players
f_DNF = [True] * 20;		#	Stores if the driver DNF
f_DSQ = [False] * 20;		#	Stores the DSQ status of drivers
f_penalties = [0] * 20;		#	Stores the total penalty time
f_totalLaps = [0] * 20;		#	Stores the total laps made by the car 
f_carPosition = [0] * 20;	#	Stores the car's final position
f_totalPitStops = [0] * 20;	#	Stores the total pitstops for drivers

#####################################################

#	Do the final calculations here

def performFinalCalculations():

	finalOutput = [[None for i in range(9)] for j in range(numOfParticipants)];

	for i in range(0,20):

		#BUGFIX HOST DNF
		#print(lapNumber[i], sessionData[3] + 1);
		if(lapNumber[i] == sessionData[3] + 1):
			f_DNF[i] = False;

		f_totalLaps[i] = lapNumber[i] - 1;
		f_penalties[i] = laptimeData[i][13];
		f_carPosition[i] = laptimeData[i][8];

	##############################################

	#Experimental Fix

	for i in f_driverNames:

		if(i.rstrip('\u0000') == ""):

			index = f_driverNames.index(i);

			del f_driverNames[index];
			del f_totalLaptimes[index];
			del f_bestLaptimes[index];
			del f_lastLaptimes[index];
			del f_DNF[index];
			del f_DSQ[index];
			del f_penalties[index];
			del	f_totalLaps[index];
			del	f_carPosition[index];
			del	f_totalPitStops[index];

			print("Empty driver entry removed");


	##############################################

	for i in range(0,numOfParticipants):
		finalOutput[i] = {'name':f_driverNames[i].rstrip('\u0000'), 'totalLapTime':f_totalLaptimes[i]*1000000, 'position':f_carPosition[i], 'laps':f_totalLaps[i], 'bestLapTime':f_bestLaptimes[i]*1000000, 'DNF':f_DNF[i], 'DSQ':f_DSQ[i], 'penalties':f_penalties[i] *1000000, 'pitstops':f_totalPitStops[i]};

	#Sort the info based on car positions
	finalOutput = sorted(finalOutput, key=lambda x:x['position']);

	#Print everything
	for i in range(0,numOfParticipants):
		print(finalOutput[i]['name']);
		print("Laps : ", finalOutput[i]['laps']);
		print("Position :", finalOutput[i]['position']);
		b, c = divmod((finalOutput[i]['totalLapTime']/1000000)%3600, 60);
		print( "Total Time: ",int(b), ":", c);
		b, c = divmod((finalOutput[i]['bestLapTime']/1000000)%3600, 60);
		print(	"Best Lap Time: ",int(b), ":", c);
		#b, c = divmod(f_lastLaptimes[i]%3600, 60);
		#print(	"Last Lap Time: ",int(b), ":", c);
		print(	"Penalties: ", (finalOutput[i]['penalties']/1000000));
		print(	"Pitstops : ", finalOutput[i]['pitstops']);
		print(	"DSQ :", finalOutput[i]['DSQ']);
		print(	"DNF :", finalOutput[i]['DNF']);
		print(" ");

	#	Create a JSON File if enabled
	if(createJsonFile):

		fileName = " ";
		fName = "telemetryData";
		fileExtension = ".json";
		timestr = time.strftime("%Y%m%d-%H%M%S");

		#Check whether name is static or dynamic
		if(createStaticFileName):
			fileName = "".join((fName,fileExtension));
		else:
			fileName = "".join((fName,timestr,fileExtension));

		with open(fileName, 'w') as f:json.dump(finalOutput, f, indent=4, separators=(',', ': '), ensure_ascii=False);

	#	Create a CSV File if enabled
	if(createCSVFile):

		fileName = " ";
		fName = "telemetryData";
		fileExtension = ".csv";
		timestr = time.strftime("%Y%m%d-%H%M%S");

		#Check whether name is static or dynamic
		if(createStaticFileName):
			fileName = "".join((fName,fileExtension));
		else:
			fileName = "".join((fName,timestr,fileExtension));

		with open(fileName, 'w') as f:writer = csv.writer(f, quoting=csv.QUOTE_ALL);writer.writerow(finalOutput);

##	Utility

def decodeString(encodedString):
	decodedString = encodedString.decode('utf-8');
	return decodedString;


#####################################################
#####################################################

## INT MAIN()

#####################################################
#####################################################

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
clientSocket.bind((IP,UDP_PORT));

while True:
	data, addr = clientSocket.recvfrom(1500); #open the client connection

	#separate the Header
	dataHeader = data[0:18];	#Header size 18 bytes

	#Break the Header into relevant information bits
	(m_packetFormat, m_packetVersion, m_packetID, m_sessionUID, m_sessionTime, m_frameIdentifier, m_playerCarIndex) = struct.unpack(headerString, dataHeader);


	#	Packet Session Data
	if(m_packetID == 1):

		sessionData = struct.unpack(sessionDataString, data[21:25]);

	# Laptime Data packet (Laptime and relevant information extracted)
	if(m_packetID == 2):
		#print(data);
		for i in range(0,20):
			laptimeData[i] = struct.unpack(laptimeDataString, data[41*i+21:41*i+62]);

			#	Store te last lap time
			f_lastLaptimes[i] = laptimeData[i][0];

			#Check if the lap changes
			if(lapNumber[i] < laptimeData[i][9]):
				f_totalLaptimes[i] += laptimeData[i][0];
				f_bestLaptimes[i] = laptimeData[i][2];
				lapNumber[i] += 1;

			#Check for DNF and DSQ Statuses
			for i in range(0,20):

				#DNF Status
				if(laptimeData[i][16] == 3):
					f_DNF[i] = False;
				#DSQ StatusC
				if(laptimeData[i][16] == 4):
					f_DSQ[i] = True;

			for i in range(0,20):

				#Check pitstop status
				if(laptimeData[i][10] and laptimeData[i][10] != 0 and prevPitStatus[i] == 0):
					f_totalPitStops[i] += 1;
					prevPitStatus[i] = laptimeData[i][10];



	# Event Data Packet (where samples are taken)
	if(m_packetID == 3):
		print("Event Data Packet Received");
		eventData = struct.unpack(eventDataString, data[21:25]);
		sessionString = decodeString(eventData[0]);
		if(sessionString == "SSTA"):
			print("Session Started!");
		if(sessionString == "SEND"):
			print("Session Complete!");
			for i in range(0,20):
				if(participantData[i][5] and decodeString(participantData[i][5]).rstrip('\u0000') != ""):
					numOfParticipants += 1;

			performFinalCalculations();

	# Participant Data Packet (Driver Names are retrieved)
	if(m_packetID == 4):
		for i in range(0,20):
			participantData[i] = struct.unpack(participantDataString, data[53*i+22:53*i+75]);
			f_driverNames[i] = decodeString(participantData[i][5]);
			if(f_driverNames[i] == "d00m™ DBaNNHD"):
				f_driverNames[i] == "Doom";

