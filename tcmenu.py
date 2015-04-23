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
			if choice > 0 and choice < iface_count:
				choice -= 1
				iface = int_array[choice]
				loop = False
                except ValueError:
                        raw_input("Wrong option selection. Entry must be [1-{0}]. Enter any key to try again.." .format (real_count))
		
def precheck ():
	# check if the user is root or sudo
	if os.getuid() != 0:
		print bcolors.FAIL
		print "***Error, must be root to execute\n"
		print bcolors.ENDC
		exit ()
	else:
		return ()

def get_bandwidth ():
	loop = True

	while loop:
        	try:
                	max_rate = int (raw_input("Please enter the maximum bandwidth allowed in kbps: "))
			return (max_rate)
        	except ValueError:
                	raw_input("Please enter a number for the maximum bandwidth.  Press Enter to try again..")

def get_latency ():
	loop = True

	while loop:
        	try:
                	max_rate = int (raw_input("Please enter the amount of latency in ms: "))
                	return (max_rate)
        	except ValueError:
                	raw_input("Please enter a number for the amount of latency.  Press Enter to try again..")

def get_latdev ():
	loop = True
	
	while loop:
        	try:
                	max_rate = int (raw_input("Please enter the deviation in latency in ms (eg. 40ms would make a range +/- 40ms: "))
                	return (max_rate)
        	except ValueError:
                	raw_input("Please enter a number for the deviation in latency.  Press Enter to try again..")

def get_ploss ():
	loop = True

	while loop:
		try:
                	max_rate = int (raw_input("Please enter the percentage of packet loss: "))
		
			if max_rate >= 0 and max_rate <= 100:
                		return (max_rate)
			else:
				raw_input("Please enter a number between 0 and 100.  Press Enter to try again..")
        	except ValueError:
                	raw_input("Please enter a number for the percentage of packet loss.  Press Enter to try again..")

def rate_limit ():
	top_limit = 1000

	max_band = get_bandwidth ()
	latency = get_latency ()
	lat_dev = get_latdev ()
	p_loss = get_ploss ()
	
	print "tc qdisc add dev {0} root handle 1:0 tbf rate {1} kbit buffer 1600 limit 3000" .format (iface, str(max_band))
	send_cmd ("tc qdisc add dev " + iface + " root handle 1:0 tbf rate " + str(max_band) + "kbit buffer 1600 limit 3000")
	print "tc qdisc add dev {0} parent 1:0 handle 10: netem delay {1}ms {2}ms 25% loss {3}% 25%" .format (iface, str(latency), str(lat_dev), p_loss)
	send_cmd ("tc qdisc add dev " + iface + " parent 1:0 handle 10: netem delay " + str(latency) + "ms " + str(lat_dev) + "ms 25% loss " + str(p_loss) + "%")

        raw_input("Press Enter to continue...")
	
def top_menu_print ():
	# Display the top level menu
	os.system('clear')
	print bcolors.HEADER
	print 15 * "-" , "Nectar Traffic Control Setup" , 15 * "-"
	print bcolors.ENDC
	print "1. Single Traffic Control Test"
	print "2. Create Batch Traffic Control impediments"
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
			rate_limit ()
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
