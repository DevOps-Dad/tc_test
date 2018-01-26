#!/usr/bin/python
#  Copyright (C) 2016  Joseph Goldberg
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

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
	# Colors to be used to display text
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
	print 5 * "-" , "Traffic Control Interface Choice " , 5 * "-"
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
	# Query the user for bandwidth limits
	loop = True

	while loop:
		try:
			max_rate = int (raw_input("Please enter the maximum bandwidth allowed in kbps: "))
			return (max_rate)
		except ValueError:
			raw_input("Please enter a number for the maximum bandwidth.  Press Enter to try again..")

def get_latency ():
	# Query the user for latency
	loop = True

	while loop:
		try:
			max_rate = int (raw_input("Please enter the amount of latency in ms: "))
			return (max_rate)
		except ValueError:
			raw_input("Please enter a number for the amount of latency.  Press Enter to try again..")

def get_latdev ():
	# Query the + or - deviation of the latency
	loop = True
	
	while loop:
		try:
			max_rate = int (raw_input("Please enter the deviation in latency in ms (eg. 40ms would make a range +/- 40ms: "))
			return (max_rate)
		except ValueError:
			raw_input("Please enter a number for the deviation in latency.  Press Enter to try again..")

def get_ploss ():
	# Query the percentage of packet loss
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

def get_duplicate ():
	# Query the percentage of duplicates
	loop = True

	while loop:
		try:
			max_rate = int (raw_input("Please enter the percentage of packets to duplicate: "))
		
			if max_rate >= 0 and max_rate <= 100:
				return (max_rate)
			else:
				raw_input("Please enter a number between 0 and 100.  Press Enter to try again..")
		except ValueError:
			raw_input("Please enter a number for the percentage of packet loss.  Press Enter to try again..")

def get_corrupt ():
	# Query corrupt packet percentage
	loop = True

	while loop:
		try:
			max_rate = int (raw_input("Please enter the percentage of packets to corrupt: "))
		
			if max_rate >= 0 and max_rate <= 100:
				return (max_rate)
			else:
				raw_input("Please enter a number between 0 and 100.  Press Enter to try again..")
		except ValueError:
			raw_input("Please enter a number for the percentage of packet loss.  Press Enter to try again..")

def get_reorder ():
	#Query re-order percentage
	loop = True

	while loop:
		try:
			max_rate = int (raw_input("Please enter the percentage of packets to delay (out of order): "))
		
			if max_rate >= 0 and max_rate <= 100:
				return (max_rate)
			else:
				raw_input("Please enter a number between 0 and 100.  Press Enter to try again..")
		except ValueError:
			raw_input("Please enter a number for the percentage of packet loss.  Press Enter to try again..")

def get_sleep ():
	# Query how long the impediment should run
	loop = True
	
	while loop:
		try:
			max_rate = int (raw_input("Please enter how many minutes to run before moving on to the next test (minutes): "))
			return (max_rate)
		except ValueError:
			raw_input("Please enter the number of minutes.  Press Enter to try again..")

def rate_limit ():
	# Single test setup
	top_limit = 1000

	clear_imp_silent ()
	
	print bcolors.OKGREEN
	print "\n\n Please answer the following questions in order to set up your impediment:\n"
	print bcolors.ENDC

	max_band = get_bandwidth ()
	latency = get_latency ()
	lat_dev = get_latdev ()
	p_loss = get_ploss ()
	duplicate = get_duplicate ()
	corrupt = get_corrupt ()
	reorder = get_reorder ()

	print bcolors.OKGREEN
	print "\n\nBelow are the tc commands that are being submitted\n"
	print bcolors.ENDC	

	print bcolors.WARNING
	print "tc qdisc add dev {0} root handle 1:0 tbf rate {1} kbit buffer 1600 limit 3000" .format (iface, str(max_band))
	send_cmd ("tc qdisc add dev " + iface + " root handle 1:0 tbf rate " + str(max_band) + "kbit buffer 1600 limit 3000")
	print "tc qdisc add dev {0} parent 1:0 handle 10: netem delay {1}ms {2}ms 25% loss {3}% 25% duplicate {4}% corrupt {5}% reorder {6}% 50%" .format (iface, str(latency), str(lat_dev), str(p_loss), str(duplicate), str(corrupt), str(reorder))
	send_cmd ("tc qdisc add dev " + iface + " parent 1:0 handle 10: netem delay " + str(latency) + "ms " + str(lat_dev) + "ms 25% loss " + str(p_loss) + "% 25% duplicate " + str(duplicate) + "% corrupt " + str(corrupt) + "% reorder " + str(reorder) + "% 50%" )
	print bcolors.ENDC

	raw_input("Press Enter to continue...")
	
def batch_mode ():
	# This is where batch mode shell scripts are created
	file_loop = True
	test_loop = True
	test_number = 0

	print bcolors.OKGREEN
	print "\n\n Please answer the following questions in order to set up your batch of impediments:\n"
	print bcolors.ENDC
	
	# Open the file, error if invalid
	while file_loop:
		try:
			filename = str (raw_input("Please enter the name of the batch file to create: "))
			f = open (filename, 'w')
			file_loop = False
		except:
			raw_input("Please enter a valid filename.  Press Enter to continue..")
	
	f.write('#!/bin/bash\n')

	# Loop and create tests until user says to stop
	while test_loop:
		yn = True
		test_number += 1

		print bcolors.WARNING
		print "\nEnter parameters for test {0}" .format (test_number)
		print bcolors.ENDC

		max_band = get_bandwidth ()
		latency = get_latency ()
		lat_dev = get_latdev ()
		p_loss = get_ploss ()
		duplicate = get_duplicate ()
		corrupt = get_corrupt ()
		reorder = get_reorder ()
		sleep = get_sleep ()

		test_line = "echo \"Running test " + str(test_number) + " for " + str(sleep) + " Minutes...\"\n"

		f.write('tc qdisc del root dev ' + iface + '\n')

		print bcolors.OKGREEN
		print "\n\nBelow are the tc commands that are being submitted to batch file {0}\n" .format (filename)
		print bcolors.ENDC	

		print bcolors.WARNING
		print "tc qdisc add dev {0} root handle 1:0 tbf rate {1} kbit buffer 1600 limit 3000" .format (iface, str(max_band))
		root_line =  "tc qdisc add dev " + iface + " root handle 1:0 tbf rate " + str(max_band) + "kbit buffer 1600 limit 3000" + "\n"
		print "tc qdisc add dev {0} parent 1:0 handle 10: netem delay {1}ms {2}ms 25% loss {3}% 25% duplicate {4}% corrupt {5}% reorder {6}% 50%" .format (iface, str(latency), str(lat_dev), str(p_loss), str(duplicate), str(corrupt), str(reorder))
		parent_line = "tc qdisc add dev " + iface + " parent 1:0 handle 10: netem delay " + str(latency) + "ms " + str(lat_dev) + "ms 25% loss " + str(p_loss) + "% 25% duplicate " + str(duplicate) + "% corrupt " + str(corrupt) + "% reorder " + str(reorder) + "% 50% \n"
		print "sleep {0}" .format (str (sleep * 60))
		sleep_line = "sleep " + str (sleep * 60) + "\n"
		print bcolors.ENDC

		f.write (test_line)
		f.write (root_line)
		f.write (parent_line)
		f.write ('tc qdisc show dev ' + iface + '\n')
		f.write (sleep_line)

		while yn:
			keep_going = str (raw_input("\nDo you wish to add more tests to the batch (y/n): "))
			
			if keep_going == "y" or keep_going == "y":
				yn = False
			elif keep_going == "n" or keep_going == "N":
				file_loop = False
				test_loop = False
				yn = False
			else:
				raw_input("Please enter Y or N  Press Enter to continue..")

	f.write('tc qdisc del root dev ' + iface)
	f.close()

	print bcolors.OKGREEN
	print "\n\nThe following batch file was created.  Please run \'sh <filename> \' as root from the command prompt to execute the tests"
	print bcolors.ENDC

	print bcolors.WARNING
	with open (filename, 'r') as fin:
		print fin.read()
	print bcolors.ENDC

	raw_input("Press Enter to continue..")

def top_menu_print ():
	# Display the top level menu
	os.system('clear')
	print bcolors.HEADER
	print 15 * "-" , "Traffic Control Setup" , 15 * "-"
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
	# Send command engine
	try:
		retcode = subprocess.call(line, shell=True)
		if retcode < 0:
			print bcolors.FAIL
			print >> sys.stderr, "Child was terminated by signal", -retcode
			print bcolors.ENDC
		else:
			print bcolors.OKGREEN
			print >> sys.stderr,"Success Code", retcode
			print bcolors.ENDC
	except OSError as e:
		print bcolors.FAIL
		print >> sys.stderr, "Execution failed:", e
		print bcolors.ENDC

def display_imp ():
	# Display impediments
	try:
		retcode = subprocess.call("tc qdisc show dev " + iface, shell=True)
		if retcode < 0:
			print bcolors.FAIL
			print >> sys.stderr, "Child was terminated by signal", -retcode
			print bcolors.ENDC
		else:
			print bcolors.OKGREEN
			print >> sys.stderr,"Success Code", retcode
			print bcolors.ENDC
	except OSError as e:
		print bcolors.FAIL
		print >> sys.stderr, "Execution failed:", e
		print bcolors.ENDC

	send_cmd ("tc class show dev " + iface)
	
	raw_input("Press Enter to continue...")

def clear_imp ():
	# Clear impediments
	try:
		retcode = subprocess.call("tc qdisc del root dev " + iface, shell=True)
		if retcode < 0:
			print bcolors.FAIL
			print >> sys.stderr, "Child was terminated by signal", -retcode
			print bcolors.ENDC
		else:
			print bcolors.OKGREEN
			print >> sys.stderr,"Success Code", retcode
			print bcolors.ENDC
	except OSError as e:
		print bcolors.FAIL
		print >> sys.stderr, "Execution failed:", e
		print bcolors.ENDC
	
	raw_input("Press Enter to continue...")

def clear_imp_silent ():
	# Clear impediments with no feedback except for critical fault
	try:
		retcode = subprocess.call("tc qdisc del root dev " + iface, shell=True)
		if retcode < 0:
			print >> sys.stderr, "Child was terminated by signal", -retcode
			raw_input("Impediment clearing failed...Press Enter to continue...")
	except OSError as e:
		print >> sys.stderr, "Execution failed:", e
		raw_input("Impediment clearing failed...Press Enter to continue...")

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
			batch_mode ()
		elif choice==3:  # Display current impediments
			display_imp ()
		elif choice==4:  # Clear all impediments
			clear_imp ()
		elif choice==5:
			pick_interface ()
		elif choice==6:
			print bcolors.OKGREEN
			print "Thank you for using the Traffic Control setup utility...Have a fantastic day!!"
			print bcolors.ENDC
			clear_imp_silent ()
			loop=False # This will make the while loop to end as not value of loop is set to False
			exit ()
		else:
			# Any integer inputs other than values 1-5 we print an error message
			raw_input("Wrong option selection. Entry must be [1-7] Enter any key to try again..")

def main ():
	precheck ()
	pick_interface ()
	clear_imp_silent ()
	top_menu ()

main()
