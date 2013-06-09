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
import bitly
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
		
	def get_favorites_list(self):
		list = []
		for x in self.config.get('Manga', 'list').splitlines():
			match = re.findall('[a-zA-z0-9 ]* ([0-9].*)', x)
			chapter_name = x.replace(' ' + match[0], '') if len(match) > 0 else x
			chapter_num = match[0] if len(match) > 0 else 0
			list.append([chapter_name, chapter_num])
		return list
		
	def output_manga_list(self, output):
		self.config.set('Manga', 'list', output)
		
		with open('application.ini', 'wb') as file:
			self.config.write(file)
		
	def update_favorites_list(self, chapter_name, chapter_num):
		favorites_list = self.get_favorites_list()
		output = '\n'.join(' '.join(str(x) for x in favorite) for favorite in favorites_list)
		output = re.sub(chapter_name + ' (.*)', chapter_name + ' ' + str(chapter_num), output)
		self.output_manga_list(output)
	
	def add_favorites_list(self, chapter_name):
		favorites_list = self.get_favorites_list()
		add_index = self.get_manga_index(chapter_name)
		if add_index == -1:
			favorites_list.append([chapter_name, 0])
			output = '\n'.join(' '.join(str(x) for x in favorite) for favorite in favorites_list)
			self.output_manga_list(output)
		else:
			print chapter_name + " is already in the list"
	
	def get_manga_index(self, chapter_name):
		favorites_list = self.get_favorites_list()
		index = -1
		for favorite in favorites_list:
			if chapter_name in favorite:
				index = favorites_list.index(favorite)
				break
		
		return index
	
	def remove_favorites_list(self, chapter_name):
		favorites_list = self.get_favorites_list()
		remove_index = self.get_manga_index(chapter_name)
		if remove_index >= 0:
			favorites_list.pop(remove_index)
			output = '\n'.join(' '.join(str(x) for x in favorite) for favorite in favorites_list)
			self.output_manga_list(output)
		else:
			print chapter_name + " has not been found in the list"
		
	def get_twitter_key(self):
		consumer_key = self.config.get('Twitter', 'consumer key')
		consumer_secret = self.config.get('Twitter', 'consumer secret')
		access_token_key = self.config.get('Twitter', 'access token key')
		access_token_secret = self.config.get('Twitter', 'access token secret')
		return consumer_key, consumer_secret, access_token_key, access_token_secret
		
	def get_bitly_key(self):
		return self.config.get('Bitly', 'key')
		
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
		#MangaWebParser().find_updates_mangapanda()
		MangaWebParser().find_updates_mangastream()
		
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
		self.url_mangapanda = 'http://www.mangapanda.com'
		self.url_mangastream = 'http://www.mangastream.com'
		
	def find_updates_mangapanda(self):
		webparser = []
		try:
			webparser = BeautifulSoup(urllib2.urlopen(self.url_mangapanda).read())
		except:
			TweetBotLog().write_log('Could not connect to Mangapanda')
		if webparser:
			for section in webparser('table', {'class' : 'updates'}):
				for row in section.findAll('tr'):
					hyperlink = row('td')[1].find('a', {'class' : 'chaptersrec'})
					if hyperlink:
						chapter_name = row('td')[1].a.strong.string
						chapter_num = re.search('^/(.*)/(.*)$', hyperlink['href']).group(2)
						url = self.url_mangapanda + hyperlink['href']
						self.check_if_update(chapter_name, chapter_num, url)
	
	def find_updates_mangastream(self):
		webparser = []
		try:
			webparser = BeautifulSoup(urllib2.urlopen(self.url_mangastream).read())
		except:
			TweetBotLog().write_log('Could not connect to Mangastream')
		if webparser:
			for section in webparser('ul', {'class' : 'freshmanga'}):
				for row in section.findAll('li'):
					hyperlink = row.a
					if hyperlink: 
						chapter_name = re.search('^(.*) (.*)$', hyperlink.string).group(1)
						chapter_num = re.search('^(.*) (.*)$', hyperlink.string).group(2)
						url = hyperlink['href']
						self.check_if_update(chapter_name, chapter_num, url)
	
	def check_if_update(self, chapter_name, chapter_num, url):
		for favorite in TweetBotConfig().get_favorites_list():
			if chapter_name in favorite and chapter_num > favorite[1]:
				TwitterAPI().post_update(chapter_name, chapter_num, BitlyAPI().shorten(url))
				TweetBotConfig().update_favorites_list(chapter_name, chapter_num)				
							
class BitlyAPI:
	def __init__(self):
		key = TweetBotConfig().get_bitly_key()
		self.api = bitly.Api(login='haeky', apikey=key)
		
	def shorten(self, url):
		return self.api.shorten(url)
		
class TwitterAPI:
	def __init__(self):
		consumer_key, consumer_secret, access_token_key, access_token_secret = TweetBotConfig().get_twitter_key()
		self.twitter = Twitter(auth=OAuth(access_token_key, access_token_secret, consumer_key, consumer_secret))
		
	def post_update(self, chapter_name, chapter_num, url):
		message = chapter_name + ' ' + chapter_num + ' is now out [' + url + ']'
		self.twitter.statuses.update(status=message)
				
if __name__ == "__main__":
	TweetBotApp().run()