''' A simple wrapper around the dropbox api'''
from __future__ import print_function

import os
import sys
import dropbox
import six
import unicodedata
import contextlib
import time
import datetime
import json

from config import (
	DROPBOX_ACCESS_TOKEN,
	ABSOLUTE_FILE_PATH,
)

@contextlib.contextmanager
def stopwatch(message):
	'''Context manager to print how long a it took to donwload the file'''
	t0 = time.time()
	try:
		yield
	finally:
		t1 = time.time()
		print('Toral elapsed time for %s: %.3f' % (message, t1 - t0))


class sanitizer_meta_class(type):

	def __new__(cls, clsname, bases, dct):

		if 'dropbox_access_token' in dct:
			val = dct.get('dropbox_access_token', None)
			if not isinstance(val, six.text_type):
				val = val.decode('utf-8')
			val = unicodedata.normalize('NFC', val)

			dct['dropbox_access_token'] = val

		if 'absolute_file_path' in dct:
			p_val = dct.get('absolute_file_path')
			if not isinstance(p_val, six.text_type):
				p_val = p_val.decode('utf-8')
			p_val = unicodedata.normalize('NFC', p_val)
			if '//' in p_val:
				p_val = p_val.replace('//', '/')	
			p_val = p_val.rstrip('/')

			dct['absolute_file_path'] = p_val

		return super().__new__(cls, clsname, bases, dct)





class DropBox(metaclass=sanitizer_meta_class):
	'''This is thin wrapper around dropbox'''
	dropbox_access_token = DROPBOX_ACCESS_TOKEN
	absolute_file_path = ABSOLUTE_FILE_PATH

	def __init__(self):
		self.dbx = dropbox.Dropbox(self.dropbox_access_token)
		self.downloaded = False
		self.datetime_mismatch = False

	def _get_prev_time(self):
		'''Query the database to see the previus updated time'''
		with open('db.json', mode='r', encoding='utf-8') as file:
			date_dct = json.load(file)
			last_modified_time = date_dct.get('last_modified_time')
			if last_modified_time:
				return datetime.datetime(*last_modified_time)
			else:
				raise ValueError('Problem occured during parsing the date and time')



	def _get_recent_file_modified_time(self):
		'''This gets the recent datetime for the file being changed'''
		filemetadata = self.dbx.files_get_metadata(self.absolute_file_path)
		return filemetadata.client_modified



	def get_arbs_html(self):
		''' Download a file.

		Return the bytes of the file, or None if it doesn't exists
		'''

		try:
			metadata, response = self.dbx.files_download(self.absolute_file_path)
		except dropbox.exceptions.HttpError as err:
			print('*** HTTP error' ,err )
			return None
		data = response.content
		self.downloaded = True
		print('Successfully downloaded...')
		return data.decode('utf-8')




