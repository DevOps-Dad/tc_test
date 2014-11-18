#!/usr/bin/python

import os
import sys
import time
import subprocess
import socket
import fcntl
import struct
import array

int_array = []
int_count = 1

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def all_interfaces():
	# Gather a list of all available interfaces
	max_possible = 128  # arbitrary. raise if needed.
	bytes = max_possible * 32
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	names = array.array('B', '\0' * bytes)
	outbytes = struct.unpack('iL', fcntl.ioctl(
		s.fileno(),
		0x8912,  # SIOCGIFCONF
		struct.pack('iL', bytes, names.buffer_info()[0])
	))[0]
	namestr = names.tostring()
	lst = []
	for i in range(0, outbytes, 40):
		name = namestr[i:i+16].split('\0', 1)[0]
		ip   = namestr[i+20:i+24]
		lst.append((name, ip))
	return lst

def format_ip(addr):
	# Format the IP address of each interface
	return str(ord(addr[0])) + '.' + \
		str(ord(addr[1])) + '.' + \
		str(ord(addr[2])) + '.' + \
		str(ord(addr[3]))

def interface_menu ():
	# Menu to pick which interface to mess with
	ifs = all_interfaces ()
	global iface_count
	iface_count = 1

	print bcolors.HEADER
        print 5 * "-" , "Nectar Traffic Control Interface Choice " , 5 * "-"
	print bcolors.ENDC

	for i in ifs:
		int_array.append (i[0])
		print "{0}. {1}\t\t{2}" .format (iface_count, i[0], format_ip(i[1]))
		iface_count += 1

        print 60 * "-"

def pick_interface ():
	# Linux interface selector
        loop=True
	global iface

        while loop:
                interface_menu ()
		real_count = iface_count - 1
                # Test that an integer has been entered
                try:
                        choice = int (raw_input("Enter your choice [1-{0}]: " .format (real_count)))
                except ValueError:
                        raw_input("Wrong option selection. Entry must be [1-{0}]. Enter any key to try again.." .format (real_count))
                        pick_interface ()
		
		if choice >0 and choice < iface_count:
			choice -= 1
			iface = int_array[choice]
			loop = False

def precheck ():
	# check if the user is root or sudo
	if os.getuid() != 0:
		print bcolors.FAIL
		print "***Error, must be root to execute\n"
		print bcolors.ENDC
		exit ()
	else:
		return ()

def top_menu_print ():
	# Display the top level menu
	print 15 * "-" , "Nectar Traffic Control Setup" , 15 * "-"
	print "1. Single Traffic Control impediment"
	print "2. Batch Traffic Control impediments"
	print "3. Display Current impediments"
	print "4. Clear all impediments"
	print "5. Change interface"
	print "6. Exit"
	print 60 * "-"

def top_menu ():  
	loop=True
  
	while loop:
		top_menu_print ()

		# Test that an integer has been entered
		try:
			choice = int (raw_input("Enter your choice [1-6]: "))
		except ValueError:
			raw_input("Wrong option selection. Entry must be [1-6]. Enter any key to try again..")
			top_menu ()

		if choice==1:     
			print "Menu 1 has been selected"
		elif choice==2:
			print "Menu 2 has been selected"
		elif choice==3:  # Display current impediments
			try:
				retcode = subprocess.call("tc qdisc show dev " + iface, shell=True)
				if retcode < 0:
					print >> sys.stderr, "Child was terminated by signal", -retcode
				else:
					print bcolors.OKGREEN
					print >> sys.stderr,"Child returned", retcode
					print bcolors.ENDC
			except OSError as e:
				print >> sys.stderr, "Execution failed:", e
		elif choice==4:  # Clear all impediments
			try:
				retcode = subprocess.call("tc qdisc del root dev " + iface, shell=True)
				if retcode < 0:
					print >> sys.stderr, "Child was terminated by signal", -retcode
				else:
					print >> sys.stderr, "Child returned", retcode
			except OSError as e:
				print >> sys.stderr, "Execution failed:", e
		elif choice==5:
			pick_interface ()
		elif choice==6:
			print "Thank you for using the Nectar Traffic Control setup utility...Have a fantastic day!!"
			loop=False # This will make the while loop to end as not value of loop is set to False
		else:
			# Any integer inputs other than values 1-5 we print an error message
			raw_input("Wrong option selection. Entry must be [1-5] Enter any key to try again..")

def main ():
#	if len(sys.argv) != 2:
#		print "Usage tcmenu <interface>\n"
#		exit ()
#	else:
#		iface = str(sys.argv[1])
	precheck ()
	pick_interface ()
	top_menu ()

main()
