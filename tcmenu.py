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

	os.system('clear')
	print bcolors.HEADER
        print 5 * "-" , "Nectar Traffic Control Interface Choice " , 5 * "-"
	print bcolors.ENDC

	for i in ifs:
		int_array.append (i[0])
		print "{0}. {1}\t\t{2}" .format (iface_count, i[0], format_ip(i[1]))
		iface_count += 1

	print bcolors.HEADER
        print 52 * "-"
	print bcolors.ENDC

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

def single_menu_print ():
	os.system('clear')
	print bcolors.HEADER
	print 15 * "-" , "Nectar TC Single Impediment" , 15 * '-'
	print bcolors.ENDC
	print "1. Latency test"
	print "2. Packet loss test"
	print "3. Jitter"
	print "4. Rate limit"
	print "5. Display current impedement"
	print "6. Clear all impedements"
	print "7. Previous menu"
        print bcolors.HEADER
        print 60 * "-"
        print bcolors.ENDC

def single_menu ():
	loop=True

        while loop:
                single_menu_print ()

                # Test that an integer has been entered
                try:
                        choice_single = int (raw_input("Enter your choice [1-7]: "))
                except ValueError:
                        raw_input("Wrong option selection. Entry must be [1-7]. Enter any key to try again..")
                        top_menu ()

                if choice_single ==1:
                        single_menu ()
                elif choice_single ==2:
                        print "Menu 2 has been selected"
                elif choice_single ==3:  # Display current impediments
                        display_imp ()
                elif choice_single ==4:  
			rate_limit ()
                elif choice_single ==5:
                        display_imp ()
                elif choice_single ==6:
			clear_imp ()
		elif choice_single ==7: # return to top menu
			top_menu ()
                else:
                        # Any integer inputs other than values 1-5 we print an error message
                        raw_input("Wrong option selection. Entry must be [1-7] Enter any key to try again..")

def rate_limit ():
	try:
		max_rate = int (raw_input("Please enter the maximum bandwidth allowed in kbps: "))
	except ValueError:
		raw_input("Please enter a number for the maximum bandwidth.  Press Enter to try again..")
		rate_limit ()

	print "tc qdisc add dev {0} handle 1: root htb default 11" .format (iface)
	send_cmd ("tc qdisc add dev " + iface + " handle 1: root htb default 11")
	print "tc class add dev {0} parent 1: classid 1:1 htb rate {1}kbps" .format (iface, max_rate)
	send_cmd ("tc class add dev " + iface + " parent 1: classid 1:1 htb rate " + str(max_rate) + "kbps")
	print "tc class add dev {0} parent 1:1 classid 1:11 htb rate {1}kbps" .format (iface, max_rate)
	send_cmd ("tc class add dev " + iface + " parent 1:1 classid 1:11 htb rate " + str(max_rate) + "kbps")
        raw_input("Press Enter to continue...")
	
	
def top_menu_print ():
	# Display the top level menu
	os.system('clear')
	print bcolors.HEADER
	print 15 * "-" , "Nectar Traffic Control Setup" , 15 * "-"
	print bcolors.ENDC
	print "1. Single Traffic Control impediment"
	print "2. Batch Traffic Control impediments"
	print "3. Display Current impediments"
	print "4. Clear all impediments"
	print "5. Change interface"
	print "6. Exit"
	print bcolors.HEADER
	print 60 * "-"
	print bcolors.ENDC

def send_cmd (line):
	try:
                retcode = subprocess.call(line, shell=True)
                if retcode < 0:
                        print >> sys.stderr, "Child was terminated by signal", -retcode
                else:
                        print bcolors.OKGREEN
                        print >> sys.stderr,"Child returned", retcode
                        print bcolors.ENDC
        except OSError as e:
                        print >> sys.stderr, "Execution failed:", e
def display_imp ():
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

	send_cmd ("tc class show dev " + iface)
	
	raw_input("Press Enter to continue...")

def clear_imp ():
        try:
		retcode = subprocess.call("tc qdisc del root dev " + iface, shell=True)
                if retcode < 0:
			print >> sys.stderr, "Child was terminated by signal", -retcode
                else:
                        print >> sys.stderr, "Child returned", retcode
        except OSError as e:
                        print >> sys.stderr, "Execution failed:", e
	
	raw_input("Press Enter to continue...")

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
			single_menu ()
		elif choice==2:
			print "Menu 2 has been selected"
		elif choice==3:  # Display current impediments
			display_imp ()
		elif choice==4:  # Clear all impediments
			clear_imp ()
		elif choice==5:
			pick_interface ()
		elif choice==6:
			print bcolors.OKGREEN
			print "Thank you for using the Nectar Traffic Control setup utility...Have a fantastic day!!"
			print bcolors.ENDC
			loop=False # This will make the while loop to end as not value of loop is set to False
			exit ()
		else:
			# Any integer inputs other than values 1-5 we print an error message
			raw_input("Wrong option selection. Entry must be [1-7] Enter any key to try again..")

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
