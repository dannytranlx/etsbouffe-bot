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
		self.config = ConfigParser.ConfigParser(allow_no_value=True)
		self.config.readfp(open('application.ini'))
		
	def get_favorites_list(self):
		return self.config.get('Manga', 'List').splitlines()
	
	def get_twitter_key(self, key):
		return self.config.get('Twitter', key)
		
	def get_bitly_key(self, key):
		return self.config.get('Bitly', key)
	
class MangaUpdatesParser:
	def get_updates_list(self):
		soup = BeautifulSoup(urllib2.urlopen('http://www.mangapanda.com').read())

		for section in soup('table', {'class' : 'updates'}):
			for row in section.findAll('tr'):
				chapters = row('td')[1].findAll('a', {'class' : 'chaptersrec'})
				manga_list = self.get_favorite_list()
				for chapter in chapters:
					link = chapter['href']
					matchObj = re.search('^/(.*)/(.*)$', link)
					name = matchObj.group(1)
					chapter_num = matchObj.group(2)
					if name in manga_list:
						print chapter_num
		
class HaekyTweetBot:
	def __init__(self):
		self.name = ""
				
if __name__ == "__main__":
	print TweetBotConfig().get_twitter_key('Consumer Key');