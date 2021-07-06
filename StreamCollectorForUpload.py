import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import csv
import enchant

#Enter Twitter API Key information
consumer_key = '####'
consumer_secret = '######'
access_token = '#########'
access_secret = '###########'

##create our csv file 'w' means open file to write into it, 'a' append
csvFile = open('tweetLocs.csv', 'a')
csvWriter = csv.writer(csvFile)
#csvWriter.writerow(["user","tweetText","latitude","longitude"])
en_us = enchant.Dict("en_US")

data_list = []
count = 0

class listener(StreamListener):
    def on_data(self, data):
        global count

        # How many tweets you want to find, could change to time based
        if count <= 2000:
            json_data = json.loads(data)

            coords = json_data["coordinates"]
            if coords is not None:

                print(coords["coordinates"])
                lon = coords["coordinates"][0]
                lat = coords["coordinates"][1]

                data_list.append(json_data)
                text = json_data['text']
                text = text.replace("\n", " ")
                text = text.replace("#", "")
                text = text.replace("@", "")
                text = ' '.join(w for w in text.split() if en_us.check(w))
                u = json_data['user']['screen_name']
                csvWriter.writerow([u,text,lat,lon])
                print(text)




                count += 1
            return True
        else:
            csvWriter.close()
            return False

    def on_error(self, status):
        print
        status


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
twitterStream = Stream(auth, listener())
# What you want to search for here
loc = [-118.4272947669417988,33.8775926399329137,-118.0044158408953194,34.1499430424126729]
twitterStream.filter(locations=loc)