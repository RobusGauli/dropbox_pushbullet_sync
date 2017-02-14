'''A main module that downloads the latest file from the dropbox account and sends 
	push notification to the client as per the situation
'''
from __future__ import print_function

import json
import os
import sys


import dropbox_client
import parser


from config import(
	APP_NAME,
	DROPBOX_ACCESS_TOKEN,
	ABSOLUTE_FILE_PATH,
	PUSH_ACCESS_TOKEN, 
	MARGIN
	)

#initialize the dropb box client



def main():
	#initialize the dropbox client
	dbx = dropbox_client.DropBox()
	#now download the arbs.html file
	html_string = dbx.get_arbs_html()
	#now parse the string and return the Arbs
	arb_parser = parser.Parser(html_string)
	#now get all the arbs
	arbs = arb_parser.get_arbs()

	#after this check to see if there is any Arb that is greater than some sepecified margin
	#and only return those arb which has desired margin
	sucessful_arbs = [arb for arb in arbs if arb.margin >= MARGIN ]
	for arb in sucessful_arbs:
		print(arb.margin)




if __name__ == '__main__':
	main()
