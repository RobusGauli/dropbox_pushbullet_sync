'''A main module that downloads the latest file from the dropbox account and sends 
	push notification to the client as per the situation
'''
from __future__ import print_function

import json
import os
import sys
import pushbullet
import re


import dropbox_client
import parser
import requests


from config import(
	APP_NAME,
	DROPBOX_ACCESS_TOKEN,
	ABSOLUTE_FILE_PATH,
	PUSH_ACCESS_TOKEN, 
	MARGIN, 
	LIMIT
	)

#initialize the dropb box client
pb = None
btc_for_1USD = ''


def convert_to_mbtc(price):
	price = price.rstrip('%').strip()
	if btc_for_1USD != '':
		float_price  = float(price) * float(btc_for_1USD) * 1000
		return '{0:.2f}mBTC'.format(float_price)
	else:
		return ''


def send_push_notification(margin, odd_type, time, data):
	'''Check to see pushbullet client is initialized'''
	#get the curretn exchange rate for  1000 USD to BTC
	if pb:
		title = odd_type + '\n' + str(margin) + '\n' + time +'\n'
		body = ''
		
		
		for option, odd, price, link in data:
			#get the mbtc amount of the price in USD
			mbtc_value = convert_to_mbtc(price)
			
			# print(type(mbtc_value))
			price = '$' + price.rstrip('%').strip()
			#convert the price to mbtc 
			
			#body = body + option + ' - ' + odd +  ' - '  + price + ' - '+ link + '\n\n'
			body = body + ' - '.join([option, odd, price, mbtc_value, link, '\n\n'])
			

		#now send the push bullet notification
		pb.push_note(title, body)
		print('Push notfication sent successfully.....')
		





def main():
	global pb, btc_for_1USD
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
	sucessful_arbs = [arb for arb in arbs if MARGIN <= arb.margin < LIMIT]
	if sucessful_arbs:
		#then initilized the push bullet cliient
		pb = pushbullet.Pushbullet(PUSH_ACCESS_TOKEN)
		
		try:
			response = requests.get('https://blockchain.info/tobtc?currency=USD&value=1')
			btc_for_1USD = response.content.decode('utf-8')
		except:
			btc_for_1USD = ''
		for arb in sucessful_arbs:
		#sometimes the result is our of the limit so
			if arb.margin :
			#get the margin value for the arb
				margin = arb.margin
				odd_type = arb.head.odd_type
				time = arb.head.time

			#now get the options
				options = arb.options
				data = []
				for option in options:
					data.append((option.option, option.odd, option.price, option.link))
			
			#now send the notification to push bullet for every arb with some condition
				send_push_notification(margin, odd_type, time, data)


		
		


if __name__ == '__main__':
	main()
