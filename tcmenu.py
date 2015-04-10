#!/usr/bin/python

import os
import sys
import time

def precheck ():
	# check if the user is root or sudo
	if os.getuid() != 0:
		print "***Error, must be root to execute\n"
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
	print "5. Exit"
	print 60 * "-"

def top_menu ():  
	loop=True
  
	while loop:
		top_menu_print ()

		# Test that an integer has been entered
		try:
			choice = int (raw_input("Enter your choice [1-5]: "))
		except ValueError:
			raw_input("Wrong option selection. Entry must be [1-5]. Enter any key to try again..")
			top_menu ()

		if choice==1:     
			print "Menu 1 has been selected"
		elif choice==2:
			print "Menu 2 has been selected"
		elif choice==3:
			print "Menu 3 has been selected"
		elif choice==4:
			print "Menu 4 has been selected"
		elif choice==5:
			print "Menu 5 has been selected"
			loop=False # This will make the while loop to end as not value of loop is set to False
		else:
			# Any integer inputs other than values 1-5 we print an error message
			raw_input("Wrong option selection. Entry must be [1-5] Enter any key to try again..")

def main ():
	precheck ()
	top_menu ()

main()
