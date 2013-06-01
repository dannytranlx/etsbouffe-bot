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
import twitter
import bitly
import ConfigParser
from bs4 import BeautifulSoup

class TweetBotConfig:
	def __init__(self):
		self.config = ConfigParser.ConfigParser(allow_no_value=1)
		self.config.readfp(open('application.ini'))
		
	def get_favorites_list(self):
		list = []
		for x in self.config.get('Manga', 'list').splitlines():
			chapter_num = re.findall('[a-zA-z0-9 ]* ([0-9].*)', x)
			chapter_name = ""
			if len(chapter_num) > 0:
				chapter_name = x.replace(' ' + chapter_num[0], '')
				chapter_num = chapter_num[0]
			else: 
				chapter_name = x
				chapter_num = 0
			list.append([chapter_name, chapter_num])
		return list
		
	def update_favorites_list(self, chapter_name, chapter_num):
		favorites_list = self.get_favorites_list()
		output = ""
		for favorite in favorites_list:
			current = ' '.join(str(x) for x in favorite)
			if chapter_name in favorite:
				current = chapter_name + ' ' + chapter_num + '\n\t'
			output += current + '\n'
		self.config.set('Manga', 'list', output)
		
		with open('application.ini', 'wb') as file:
			self.config.write(file)
			
	
	def get_twitter_key(self, key):
		return self.config.get('Twitter', key)
		
	def get_bitly_key(self):
		return self.config.get('Bitly', 'key')
	
class MangaWebParser:
	def __init__(self):
		self.url = 'http://www.mangapanda.com'
	def find_updates(self):
		soup = BeautifulSoup(urllib2.urlopen(self.url).read())
		for section in soup('table', {'class' : 'updates'}):
			for row in section.findAll('tr'):
				chapter_name = row('td')[1].a.strong.string
				hyperlink = row('td')[1].findAll('a', {'class' : 'chaptersrec'})
				favorites_list = TweetBotConfig().get_favorites_list()
				repository = hyperlink[0]['href']
				matchObj = re.search('^/(.*)/(.*)$', repository)
				chapter_num = matchObj.group(2)
				for favorite in favorites_list:
					if chapter_name in favorite and chapter_num > favorite[1]:
						print BitlyAPI().shorten(self.url + repository)
						#TweetBotConfig().update_favorites_list(chapter_name, chapter_num)
							
class BitlyAPI:
	def __init__(self):
		key = TweetBotConfig().get_bitly_key()
		self.api = bitly.Api(login='haeky', apikey=key)
		
	def shorten(self, url):
		return self.api.shorten(url)
		
class TwitterAPI:
	def __init__(self):
		consumer_key = TweetBotConfig().get_twitter_key('consumer key')
		consumer_secret = TweetBotConfig().get_twitter_key('consumer secret')
		access_token_key = TweetBotConfig().get_twitter_key('access token key')
		access_token_secret = TweetBotConfig().get_twitter_key('access token secret')
		self.api = twitter.Api(consumer_key, consumer_secret, access_token_key, access_token_secret)
		print self.api.VerifyCredentials()
	
	def post_update(self, message):
		self.api.PostUpdate(message)
				
if __name__ == "__main__":
	MangaWebParser().find_updates()
	TwitterAPI().post_update('TEST')