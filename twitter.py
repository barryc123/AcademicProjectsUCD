"""
Functions used to connect to and get data from Twitter's API
"""
import time
from typing import List

import pandas as pd
import tweepy

from Smurfit.ValueInvesting.clean_data import clean_tweet, get_subjectivity, get_polarity, get_sentiment
from Smurfit.ValueInvesting.tweepy_auth import AUTHENTICATION_TOKEN_BEAR_TOKEN


def twitter_analysis(tickers: List, start_time: pd.Timestamp, end_time: pd.Timestamp):
    """
    Function to get data from Twitter and perform sentiment analysis using TextBlob
    """
    # activate client
    client = tweepy.Client(AUTHENTICATION_TOKEN_BEAR_TOKEN, wait_on_rate_limit=True)

    # Dataframe to store the number of pos,neg, neutral tweets for each stock
    sentiment_counter_df = pd.DataFrame(columns=['Stock', 'Positive', 'Neutral', 'Negative'])

    # loop through tickers and get sentiment data
    for ticker in tickers:
        search_term = '$' + ticker
        ticker_tweets = []
        for response in tweepy.Paginator(client.search_all_tweets,
                         query=search_term + ' -is:retweet lang:en',
                         user_fields=['username', 'public_metrics', 'description', 'location'],
                         tweet_fields=['created_at', 'geo', 'public_metrics', 'text'],
                         expansions='author_id',
                         start_time=start_time,
                         end_time=end_time,
                         max_results=500):
            time.sleep(2)
            ticker_tweets.append(response)

        result = []
        user_dict = {}

        # Loop through each response object
        for response in ticker_tweets:
            # Take all the users, and put them into a dictionary of dictionaries with the info want to keep
            for user in response.includes['users']:
                user_dict[user.id] = {'username': user.username,
                                      'followers': user.public_metrics['followers_count'],
                                      'tweets': user.public_metrics['tweet_count'],
                                      'description': user.description,
                                      'location': user.location
                                      }
            for tweet in response.data:
                # For each tweet, find the author's information
                author_info = user_dict[tweet.author_id]
                # Put all the information want to keep in a single dictionary for each tweet
                result.append({'author_id': tweet.author_id,
                               'username': author_info['username'],
                               'author_followers': author_info['followers'],
                               'author_tweets': author_info['tweets'],
                               'author_description': author_info['description'],
                               'author_location': author_info['location'],
                               'text': tweet.text,
                               'created_at': tweet.created_at,
                               'retweets': tweet.public_metrics['retweet_count'],
                               'replies': tweet.public_metrics['reply_count'],
                               'likes': tweet.public_metrics['like_count'],
                               'quote_count': tweet.public_metrics['quote_count']
                               })

        # Change this list of dictionaries into a dataframe
        test_df = pd.DataFrame(result)
        tweets_df = pd.DataFrame(test_df['text'])
        tweets_df.rename(columns={'text': 'Tweets'}, inplace=True)

        # clean the tweets
        tweets_df["Cleaned_Tweets"] = tweets_df["Tweets"].apply(clean_tweet)

        # Create two new columns called Subjectivity and pPlarity
        tweets_df['Subjectivity'] = tweets_df['Cleaned_Tweets'].apply(get_subjectivity)
        tweets_df['Polarity'] = tweets_df['Cleaned_Tweets'].apply(get_polarity)

        # Create a column to store the text sentiment
        tweets_df['Sentiment'] = tweets_df['Polarity'].apply(get_sentiment)

        positive_count = 0
        neutral_count = 0
        negative_count = 0

        try:
            # Count the number of pos, neutral and neg tweets
            positive_count = tweets_df.Sentiment.value_counts().Positive
            neutral_count = tweets_df.Sentiment.value_counts().Neutral
            negative_count = tweets_df.Sentiment.value_counts().Negative
        except:
            pass

        # Add num of pos, neutral and neg tweets to dataframe
        sentiment_counter_df.loc[sentiment_counter_df.shape[0]] = (search_term, positive_count, neutral_count, negative_count)

        return sentiment_counter_df
