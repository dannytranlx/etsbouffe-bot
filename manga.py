# -*- coding: utf-8 -*-

# Copyright (c) 2013, Laurent Dang <dang.laurent@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import urllib2
import re
import os 
import oauth2
import ConfigParser
import argparse
from twitter import *
from datetime import datetime
from bs4 import BeautifulSoup

class TweetBotConfig:
	def __init__(self):
		path = os.path.dirname(os.path.realpath(__file__))
		if path:
			os.chdir(path)
		self.config = ConfigParser.ConfigParser(allow_no_value=1)
		self.config.readfp(open('application.ini', 'a+'))
			
		
	def get_twitter_key(self):
		consumer_key = self.config.get('Twitter', 'consumer key')
		consumer_secret = self.config.get('Twitter', 'consumer secret')
		access_token_key = self.config.get('Twitter', 'access token key')
		access_token_secret = self.config.get('Twitter', 'access token secret')
		return consumer_key, consumer_secret, access_token_key, access_token_secret
	
	def get_twitter_handle(self, name):
		if self.config.has_option('TwitterHandlers', name):
			return self.config.get('TwitterHandlers', name)
		return name
		
class TweetBotLog:
	def __init__(self):
		path = os.path.dirname(os.path.realpath(__file__))
		if path:
			os.chdir(path)
		self.file = open('application.log', 'a+')
		
	def __del__(self):
		self.file.close()
		
	def write_log(self, message):
		d = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.file.write(d + ':\t\t' + message + '\n')
	
class TweetBotApp:
	def __init__(self):
		self.argparse = self.build_args()
		
	def run(self):
		args = self.argparse.parse_args()
		args.func(args);
		
	def build_args(self):
		parser = argparse.ArgumentParser(description="This is a twitter bot that will tweet when a new chapter comes out")
		subparsers = parser.add_subparsers(dest="command", help='Sub-commands help')
		
		#List
		parser_list = subparsers.add_parser('list', help='List all the mangas that are being watched')
		parser_list.set_defaults(func=self.command_list)
		
		#Add
		parser_add = subparsers.add_parser('add', help='Add a new manga to the watch list')
		parser_add.add_argument('manga_name', action="store", nargs="?", type=str, help='Name of the manga you want to add to the list')
		parser_add.set_defaults(func=self.command_add)
		
		#Fetch
		parser_fetch = subparsers.add_parser('fetch', help='Fetch all the updates from mangapanda')
		parser_fetch.set_defaults(func=self.command_fetch)
		
		#Remove
		parser_remove = subparsers.add_parser('remove', help='Remove a manga from the watch list')
		parser_remove.add_argument('manga_name', action="store", nargs="?", type=str, help='Name of the manga you want to remove from the list')
		parser_remove.set_defaults(func=self.command_remove)
		
		return parser
		
	def command_list(self, args):
		for favorite in TweetBotConfig().get_favorites_list():
			print favorite[0] + ' ' + favorite[1]
			
	def command_fetch(self, args):
		MangaWebParser().find_updates()
		
	def command_remove(self, args):
		if args.manga_name:
			TweetBotConfig().remove_favorites_list(args.manga_name)
		else:
			print self.argparse.print_help()
		
	def command_add(self, args):
		if args.manga_name:
			TweetBotConfig().add_favorites_list(args.manga_name)
		else:
			print self.argparse.print_help()
		
class MangaWebParser:
	def __init__(self):
		self.url_mtlcity = 'http://cuisinederue.org/calendrier-site-de-la-ville/'
		
	def find_updates(self):
		webparser = []
		try:
			webparser = BeautifulSoup(urllib2.urlopen(self.url_mtlcity).read())
		except:
			TweetBotLog().write_log('Could not connect to cuisinederue.org website')
		if webparser:
			section = webparser('table', {'class' : 'evtsmtl'})[datetime.today().weekday()]
			# Parsing rows to find venue
			for row in section.findAll('tr'):
				for td in row.findAll('td', {'class':'site'}):
					if td.find('a').string.find('Rue Peel') != -1: # We found the good venue
						slot = row.findAll('td')

						trucks = []
						am = []
						noon = []
						pm = []
						
						times = []
						am_time = '[7h-10h] '
						noon_time = '[11h-14h30] '
						pm_time = '[15h-18h] '

						for li in slot[1].findAll('li'):
							am.append(TweetBotConfig().get_twitter_handle(li.string.encode('utf8')))
							if am_time not in times: times.append(am_time)

						for li in slot[2].findAll('li'):
							noon.append(TweetBotConfig().get_twitter_handle(li.string.encode('utf8')))
							if noon_time not in times: times.append(noon_time)

						for li in slot[3].findAll('li'):
							pm.append(TweetBotConfig().get_twitter_handle(li.string.encode('utf8')))
							if pm_time not in times: times.append(pm_time)

						if am: trucks.append(am)
						if noon: trucks.append(noon)
						if pm: trucks.append(pm)

						# Post to Twitter
						if trucks:
							TwitterAPI().post_update(trucks, times)
						else:
							TwitterAPI().post_notruck()			
		
class TwitterAPI:
	def __init__(self):
		consumer_key, consumer_secret, access_token_key, access_token_secret = TweetBotConfig().get_twitter_key()
		self.twitter = Twitter(auth=OAuth(access_token_key, access_token_secret, consumer_key, consumer_secret))
		
	def post_update(self, trucks, times):
		message = 'Au menu aujourd\'hui...\n'

		message += '\n'.join(times[idx] + ' & '.join(truck for truck in trucks[idx]) for idx, time in enumerate(times))
		
		if len(message)<140-14:
			message += '\nBonne appétit!'

		if len(message)<140-11:
			message += ' #etsbouffe';

		print message

		self.twitter.statuses.update(status=message)

	def post_notruck(self):
		message = 'Pas de camion aujourd\'hui :( #etsbouffe'

		print message

		self.twitter.statuses.update(status=message)
				
if __name__ == "__main__":
	TweetBotApp().run()