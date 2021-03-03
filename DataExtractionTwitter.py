import sys
import subprocess
import tweepy
import pandas as pd

cmd_line = sys.argv[1]

#print("TweetId Extraction started")

p1 = subprocess.Popen(['snscrape twitter-search " %s since:2020-01-01 until:2020-01-02" > collected_tweets.txt' %(cmd_line)], shell = True)

try:
    p1.wait(timeout=10)
except subprocess.TimeoutExpired:
    p1.kill()


credentials_df = pd.read_csv('credentials.csv',header=None,names=['Name','Key'])
consumer_key = credentials_df.loc[credentials_df['Name']=='consumer_key','Key'].iloc[0]
consumer_secret = credentials_df.loc[credentials_df['Name']=='consumer_secret','Key'].iloc[0]
access_token = credentials_df.loc[credentials_df['Name']=='access_token','Key'].iloc[0]
access_token_secret = credentials_df.loc[credentials_df['Name']=='access_secret','Key'].iloc[0]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

tweet_url = pd.read_csv("collected_tweets.txt", index_col= None, header = None, names = ["links"])

af = lambda x: x["links"].split("/")[-1]
tweet_url['ID'] = tweet_url.apply(af, axis=1)

idlist = tweet_url['ID'].tolist()
total_tweets = len(idlist)
batch = (total_tweets - 1) // 50 + 1
#print("TweetId Extraction finished")
#print(total_tweets)

def extract_tweets(tweet_ids):
    status = api.statuses_lookup(tweet_ids, tweet_mode= "extended")
    df = pd.DataFrame()
    for tweet in status:
        tweet_element = {"tweet_ID": tweet.id,
                         "username": tweet.user.screen_name,
                         "tweet": tweet.full_text,
                         "date": tweet.created_at,
                         "coordinates":tweet.coordinates,
                         "location": tweet.user.location,
                         "place": tweet.place}

        df = df.append(tweet_element, ignore_index=True)
    df.to_csv("extracted_tweets.csv", mode="a")

#print("Tweet Extraction started")

for i in range(batch):
        extract_batch = idlist[i*50:(i+1)*50]
        data = extract_tweets(extract_batch)

#print("Tweet Extraction finished")

#-----------------Sentiment Analysis ------------------------#

import pandas as pd
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from textblob import TextBlob
from textblob import Word


df1 = pd.read_csv('extracted_tweets.csv',lineterminator='\n')
df_total = pd.concat([df1])
Corpus = df_total.copy()

df_total['lowercase']=df_total['tweet'].apply(lambda x: " ".join(word.lower() for word in x.split()))
df_total['punctuation']=df_total['lowercase'].str.replace('[^\w\s]','')
stop_words=stopwords.words('english')

df_total['stopwords']=df_total['punctuation'].apply(lambda x: " ".join(word for word in x.split()if word not in stop_words))
df_total['lemmatize']=df_total['stopwords'].apply(lambda x:" ".join(Word(word).lemmatize() for word in x.split()))
df_total['polarity']=df_total['lemmatize'].apply(lambda x: TextBlob(x).sentiment[0])## just got polarity

from wordcloud import WordCloud
all_words = ' '.join([text for text in df_total['lemmatize']])
wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)
plt.figure(figsize=(10, 7))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.savefig("wordcloud.png")



tweetssorted = df_total.sort_values(by='polarity', ascending=True)
neg_tweets = tweetssorted[:10]
neg_tweets1 = neg_tweets['lemmatize']

tweetssorted = df_total.sort_values(by='polarity', ascending=False)
pos_tweets = tweetssorted[:10]
pos_tweets1 = pos_tweets['lemmatize']
pos_tweets2 = pos_tweets[['tweet_ID','username','lemmatize','polarity']].copy()

neg_tweets.to_csv("/Users/Aparna/AWSUpload/auth_django/neg_tweets.csv")
pos_tweets2.to_csv("/Users/Aparna/AWSUpload/auth_django/postive_tweets.csv", index=False)

data = df_total.dropna()
pol = df_total['polarity']
top20 = data['location'].value_counts()
top20 = top20[0:20]
top20 = top20.to_frame().reset_index()
top20.rename(columns = {'index':'location','location':'counts'}, inplace = True)
top20.to_csv('top20locationtweeting.csv')
pol.to_csv('/Users/Aparna/AWSUpload/auth_django/polarity.csv')

#
# sns.barplot(y="location", x="counts", data=top20)
# sns.set(rc={'figure.figsize':(15,10)})
# plt.savefig("locations_img.png")

#print("Sentiment Analysis Complete")
