ETSBouffe-Bot
=================

This is a twitter bot that will tweet daily the schedule of food truck in front of ÉTS.
http://www.twitter.com/etsbouffe

## Usage
The `fetch` command will go parse the http://cuisinederue.org/ food truck schedule and return which and when food trucks will be at Peel / Notre-Dame. Afterwards, ETSBouffe-Bot will connect to the [@etsbouffe](http://twitter.com/etsbouffe) twitter account and send a tweet with today's schedule.

	$ python etsbouffe.py fetch

## Crontab
This script has been set up on a Raspberry Pi with Crontab to run daily at 7am.
	
	00 07 * * * python /home/pi/etsbouffe.py fetch

## Configuration
Obviously, the web site parsing has been writing to parse that specific table on http://cuisinederue.org/, but the Twitter account can be changed in the [application.ini](../master/application.ini.exemple) file.

	[Twitter]
	consumer key = 
	consumer secret = 
	access token key = 
	access token secret = 
	
You can get your Twitter API keys on https://dev.twitter.com/.

Twitter handlers for food trucks can be also updated in [application.ini](../master/application.ini.exemple) under **[TwitterHandlers]**

	[TwitterHandlers]
	Boîte à Fromages = @boiteafromages
	Chaud Dogs = @Chauddogs
	Cuisine Lucky’s Truck = @LuckysTruckMTL
	Gaufrabec = @GAUFRABEC
	Grumman 78 = @Grumman78
	Landry & filles = @landryetfilles
	Le Gourmand Vagabond = @GourmandVagabon
	Le Super Truck = @SuperTruckMTL
	Le Tuktuk = @letuktuk
	Nomade So6 par Accords = @nomadeso6
	P.A. & Gargantua = @pa_gargantua
	Route 27 = @Route27foodtruc
	Roux = @ROUXfoodtruck
	St-Viateur Bagel = @StViateurBagel
	Winneburger = Winneburger (@NouveauPalais)
	Zoe’s = @zoesfoodtruck
	
## Thanks

Big thanks to [Laurent Dang](http://www.github.com/haeky/)!
