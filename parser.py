import os
import sys
import bs4
import unicodedata
import itertools

from collections import namedtuple

Head = namedtuple('Head', 'odd_type margin time')
Option = namedtuple('Option', 'option odd price link')

Arb = namedtuple('Arb', 'head options margin')
class Parser(object):
	'''This class is used for parsing th raw html from the file downloaded from the dropbox'''

	def __init__(self, html_string):
		self.root = bs4.BeautifulSoup(html_string, 'html.parser')
		self.arbs_trs = self.get_tr_tags()

	def get_tr_tags(self):
		if self.root:
			trs = self.root.find_all('tr')
			#now filter the tag to the correct points
			trs = trs[2: ]
			#now  group all the trs tags that that resemblence each arbs
			_ite = itertools.groupby(trs, lambda tag : len(tag.contents) < 4)
			#now only accumulate those trs which has a false value i.e every arbs <tr>
			arbs_trs = []
			for key, val in _ite:
				tr = []
				for v in val:
					if key == False:
						tr.append(v)
				if tr:
					arbs_trs.append(tr)
			return arbs_trs
			

	def handle_header(self, tr):
		headers = [td.get_text() for td in tr.contents if not isinstance(td, bs4.element.NavigableString)]
		#now unpack
		_, odd_type, margin, *_, date = headers
		#returns the named tuple of Header for header <tr>
		return Head(odd_type, margin, date)

	def handle_other_trs(self, trs):
		options = []
		for tr in trs:
			alist = [td.get_text() for td in tr if not isinstance(td, bs4.element.NavigableString)]
			op, odd, price, *_, link = alist
			options.append(Option(op, odd, price, link))
		return options


	def get_arbs(self):
		total_arbs = []
		for arb_tr in self.arbs_trs:
			Head = self.handle_header(arb_tr[0])
			options = self.handle_other_trs(arb_tr[1:])
			arb = Arb(Head, options, Head.margin)
			total_arbs.append(arb)
		return total_arbs









			

	