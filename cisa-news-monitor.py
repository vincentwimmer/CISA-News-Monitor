"""
Lately I've been creating A LOT of monitors to check on things all over the internet.

Here's a very basic monitor to check CISA.gov for news updates.

This should provide you with everything you need as a foundation for your own monitor.

	-Vince

Written in Python3
"""

#Here we use all native libraries. This code is meant to work on anything.
# First is Requests, used for making connections to the internet and getting or sending data.
import requests
# Next is Re, this is a VERY powerful library for maniuplating text and other things.
import re
# Lastly, Time. Only used for it's Sleep funtion in this case.
import time

#Here we set the URL that we'll be monitoring.
url = "https://us-cert.cisa.gov/"

#HTTP/HTTPS Requests often require headers to complete the request, depending on the server.
#These headers mimic a request from Google Chrome.
headers = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "en-US,en;q=0.5",
	"Connection": "keep-alive",
	"TE" : "Trailers",
	"Upgrade-Insecure-Requests": "1", 
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
	}

#Now we create a variable for the delay in seconds between Requests.
sleepTime = 180

#This funtion will be handling our HTML parsing.
# Most people will use BeautifulSoup for this but
# that'll add on to processing time and I prefer
# to utilize native libraries wherever I can.
def getInfo(postInfo):
	#Set a blank list to avoid refrencing errors.
	alertData = []

	#Set blank Variables to also avoid refrencing errors.
	alertImgSrc = None
	alertTitle = None
	alertDate = None
	alertURL = None

	#Before we do anything, lets check if the "latest post" <div> exists.
	# If it doesn't, postInfo.find will return a "-1"
	if postInfo.find('<div class="col col-xs-12 col-sm-12 col-md-6 col-lg-3 ">') != -1:

		#If we find the <div> we can assign "pos" to the exact character placement in the full text by number.
		pos = postInfo.find('<div class="col col-xs-12 col-sm-12 col-md-6 col-lg-3 ">')

		#Now we can assign "alertHTML" a smaller chunk of raw HTML code to work with.
		# This way we don't have to work with an ENTIRE page of HTML and 
		# instead just the <div>'s HTML we need.
		# The numbers here might need some explanation:
		# "pos" is a number as mentioned above. Let's pretend it's 9000 in this case.
		# +55 is the length of our search string which moves the "cursor" to the end of the search string.
		# +1000 is the rough estimate of the block of HTML we want
		# So by saying "(pos+55) : (pos+1000)" we're saying select everything 
		# AFTER '<div class="col col-xs-12 col-sm-12 col-md-6 col-lg-3 ">' and up to 1000 characters.
		alertHTML = (postInfo[(pos+55) : (pos+1000)])

		####
		#For the next four IF statements we search for a string,
		# if the string exists, we sift out what we don't want and keep the gold.
		# Once done, the parsed info is assigned to a variable we created above.
		# ie. alertImgSrc, alertTitle, etc..

		#Parse the post's Image Url
		if alertHTML.find('<img src="') != -1:
			getItemImg = alertHTML.find('<img src="')
			alertImgParse = (alertHTML[(getItemImg+10) : (getItemImg+150)])
			alertImgFixed = re.split(r'<|\"', alertImgParse)
			alertImgSrc = "https://us-cert.cisa.gov/"+alertImgFixed[0]

		#Parse the post's Title
		if alertHTML.find('<h4 class="field-content entry-title">') != -1:
			getItemTitle = alertHTML.find('<h4 class="field-content entry-title">')
			alertTitleParse = (alertHTML[(getItemTitle+38) : (getItemTitle+500)])
			alertTitleFixed = re.split(r'<|\"|title=', alertTitleParse)
			alertTitle = alertTitleFixed[5]

		#Parse the post's Date
		if alertHTML.find('<div class="entry-date"><span>') != -1:
			getItemDate = alertHTML.find('<div class="entry-date"><span>')
			alertDateParse = (alertHTML[(getItemDate+30) : (getItemDate+100)])
			alertDateFixed = re.split(r'<|\"|\n', alertDateParse)
			alertDate = alertDateFixed[0]

		#Parse the post's Direct URL
		if alertHTML.find('<a href="') != -1:
			getItemURL = alertHTML.find('<a href="')
			alertURLParse = (alertHTML[(getItemURL+9) : (getItemURL+200)])
			alertURLFixed = re.split(r'<|\"|\n', alertURLParse)
			alertURL = "https://us-cert.cisa.gov/"+alertURLFixed[0]

		#Now the variables are brought together as a list and assigned to alertData.
		# This makes handling the data very clean and easy.
		alertData = ([alertTitle, alertDate, alertImgSrc, alertURL])
	
	#This is where the sum of everything we just accomplished gets pushed back to
	# the newPost variable in the Main function.
	# See what I mean about clean and easy?
	return alertData
	
#This is our main loop/function
def Main(url):
	#Set empty List
	oldPost = [None]

	#Run forever..
	while True:
		#We can use a try/except statement to catch request failures as well as
		# keeping the loop going instead of breaking on errors.
		try:
			#Make GET request to CISA using headers from above.
			getLatestPost = requests.get(url, headers=headers)

			#Send text from request to our parsing function and wait for returned data.
			newPost = getInfo(getLatestPost.text)

			#Check if fetched data differs from previous fetch.
			if newPost[0] != oldPost[0]:

				#Post these prints to Discord, Twitter, or even Slack? Up to you!
				print(newPost[0])
				print(newPost[1])
				print(newPost[2])
				print(newPost[3])

				#Clear and replace old fetch with new fetch
				oldPost.clear()
				oldPost = newPost

				#Let's not spam the government, take a nap.
				time.sleep(sleepTime)
		except:
			#Let's wait 30sec and try again.
			time.sleep(30)

#Bring monitor online.
Main(url)
