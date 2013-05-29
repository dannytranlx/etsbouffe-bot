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
from bs4 import BeautifulSoup
from lib.manga import Manga

def get_updates_list():
	soup = BeautifulSoup(urllib2.urlopen('http://www.mangapanda.com').read())

	for section in soup('table', {'class' : 'updates'}):
		for row in section.findAll('tr'):
			chapters = row('td')[1].findAll('a', {'class' : 'chaptersrec'})
			for chapter in chapters:
				link = chapter['href']
				matchObj = re.search('^/(.*)/(.*)$', link)
				name = matchObj.group(1)
				chapter = matchObj.group(2)
				manga = Manga(name, chapter)
				print manga.Name, manga.Chapter
				
def get_manga_list():
	path = os.path.dirname(__file__)
	conf = os.path.join(path, "conf", "list")
	mangas = open(conf, 'r').read().splitlines()
	return mangas
				
if __name__ == "__main__":
	print get_manga_list()