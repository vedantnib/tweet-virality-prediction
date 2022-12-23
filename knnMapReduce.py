from turtle import distance
from typing_extensions import final
import tweepy
import pandas as pd
import numpy as np
import json
from textblob import TextBlob
import re
import json
from pyspark.sql import SparkSession
import random
import pyspark.sql.functions as sparkSqlFunctions
from pyspark.sql.types import *
import warnings
warnings.filterwarnings(action='ignore')
from sklearn.utils import shuffle
import math
import json
import twitter_credentials
import followersData
import os


spark = SparkSession.builder.appName("spark-stream").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")


def preprocess_tweets(tweetsData):
    entities = pd.DataFrame.from_dict(tweetsData['entities'])
    tweetsData['hashtags'] = tweetsData.apply(lambda x: x['entities']['hashtags'], axis=1)

    tweetsData['d'] = pd.DataFrame.from_dict(tweetsData['hashtags'])
    tweetsData['hashtag_counts'] = tweetsData['d'].str.len().to_frame()
    tweetsData['user_mentions'] = tweetsData.apply(lambda x: x['entities']['user_mentions'], axis=1)
    tweetsData['a'] = pd.DataFrame.from_dict(tweetsData['user_mentions'])
    tweetsData['tagged_user_count'] = tweetsData['a'].str.len().to_frame()
    tweetsData['urls'] = tweetsData.apply(lambda x: x['entities']['urls'], axis=1)
    tweetsData['b'] = pd.DataFrame.from_dict(tweetsData['urls'])
    tweetsData['urls_count'] = tweetsData['b'].str.len().to_frame()
    tweetsData['tweet_len'] = tweetsData['text'].str.len()
    user = pd.DataFrame.from_dict(tweetsData['user'])
    tweetsData['followers_count'] = tweetsData.apply(lambda x: x['user']['followers_count'], axis=1)
    tweetsData = tweetsData[['tagged_user_count','urls_count', 'hashtag_counts','tweet_len','followers_count','retweet_count']]
    tweetsData['isViral'] = 0
    tweetsData.loc[tweetsData['retweet_count'] > 15, 'isViral'] = 1
    return shuffle(tweetsData)

def preprocess_tweet(raw_data):
    try:
        data = json.loads(raw_data)['data']
        id = data['author_id']
        tweet_len = len(data['text'])
        tagged_user_count = 0 
        urls_count = 0
        hashtag_counts=0
        followers_count= 0
        context_annotations = "NotAnnotatedTweet"
        try:
            for i in data['context_annotations']:
                context_annotations = i['domain']['name']
                break
        except:
            print("KeyError in context annotation as field not found in tweet response!")
        try :
            tagged_user_count = len(data['entities']['mentions'])
        except:
            print("mentions not found")
        try :
            urls_count = len(data['entities']['urls'])
        except:
            print("No URLS found")
        try :
            hashtag_counts = len(data['entities']['hashtags'])
        except:
            print("No Hashtags found")
        followers_count = followersData.main(id, twitter_credentials.bearerToken)
    except KeyboardInterrupt:
        print("Tweets Collected")
    return tagged_user_count,urls_count, hashtag_counts,tweet_len,followers_count,context_annotations
    

def getLabelFromKNeighbours(result, k):
    print("getLabelFromKNeighbours " +str(getLabelFromKNeighbours))
    zero_count = 0
    one_count = 0
    for element in result[:k]:
        if element[1] == 0:
            zero_count += 1
        else:
            one_count += 1
    if zero_count > one_count:
        return 0
    else:
        return 1

def eDistance(x1, y1, z1, a1, b1, x2,y2, z2, a2, b2):
    distance = math.sqrt(((x1-x2)**2) + (y1-y2)**2 + (z1-z2)**2 + (a1-a2)**2 + (b1 - b2)**2)
    return distance 


def KNN_Classifier(tweetsData_final, tagged_user_count, hashtag_count, link_count, tweet_len, followers_count, k = 3):
    resulting_labels = {0: "NotViral", 1: "Viral"}
    allTweetsDF = spark.createDataFrame(tweetsData_final)
    rdd = allTweetsDF.rdd
    result = rdd\
        .map(
            lambda ele: (
                eDistance(
                    ele[0], 
                    ele[1], 
                    ele[2], 
                    ele[3], 
                    ele[4], 
                    tagged_user_count, 
                    link_count,
                    hashtag_count,  
                    tweet_len, 
                    followers_count), 
                ele[6]))\
                .sortByKey()\
                    .collect()
    model_prediction = resulting_labels[getLabelFromKNeighbours(result, k)]
    return model_prediction

# path = os.cwd()
tweetsData = pd.read_json("/Users/vedantnibandhe/Desktop/Bigdata/random_tweets.json", lines = True)
tweetsData_final = preprocess_tweets(tweetsData)
    
class TwitterListener(tweepy.StreamingClient):
    def on_data(self, raw_data):
        try:
            tagged_user_count, link_count, hashtag_count,tweet_len,followers_count,context_annotations = preprocess_tweet(raw_data)
            model_prediction = KNN_Classifier(tweetsData_final, tagged_user_count, hashtag_count, link_count,tweet_len,followers_count, 3)
            print("model_prediction:", model_prediction)
            resultDict = {}
            resultDict["prediction"] = [model_prediction]
            newDict = {}
            newDict["context"] = [context_annotations]
            resultDF = pd.DataFrame.from_dict(resultDict)
            sparkDF = spark.createDataFrame(resultDF)            
            resultDF2 = pd.DataFrame.from_dict(newDict)            
            sparkDF2 = spark.createDataFrame(resultDF2)
            query = sparkDF.selectExpr("prediction AS value")\
                .write\
                    .format("kafka")\
                        .option("kafka.bootstrap.servers", "localhost:9092")\
                            .option("topic", "abc")\
                                .save()
            query2 = sparkDF2.selectExpr("context AS value")\
                .write\
                    .format("kafka")\
                        .option("kafka.bootstrap.servers", "localhost:9092")\
                            .option("topic", "abc")\
                                .save()
         
        except KeyboardInterrupt:
            print("Tweets Collected")
        return True
    
    def on_error(self, status):
        if status == 420:
            return False
        print(status)

stream = TwitterListener(twitter_credentials.bearerToken)
stream.sample()
stream.filter(tweet_fields=[
        "context_annotations",
        "author_id",
        "entities",
        "id",
        "text"])