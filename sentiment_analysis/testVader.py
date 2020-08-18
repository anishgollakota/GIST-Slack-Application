from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import json
from textblob import TextBlob
import re
import string
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


tokens = {}
with open('configs.json') as json_data:
    tokens = json.load(json_data)

slack_events_adapter = SlackEventAdapter(tokens.get("slack_signing_secret"), "/slack/events")
slack_client = SlackClient(tokens.get("slack_bot_token"))

vader_analyzer = SentimentIntensityAnalyzer()


@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    channel = message["channel"]
    user = "<@%s>" % message["user"]
    message_text = clean_text(message.get('text'))
    sentiment_score = calculate_sentiment_score(message_text)
    emotion = calculate_emotion(sentiment_score)
    compound_score = sentiment_score['compound']
    if message.get("subtype") is None and message["user"]!="U0160T55TD2":
        send_message = str(user) + " seems " + emotion
    slack_client.api_call("chat.postMessage", channel=channel, text=send_message)

@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

def clean_text(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    return remove_stop_words(text)

def remove_stop_words(text):
    if len(text.split()) < 2:
        return text
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    tokens_without_stopwords = [word for word in tokens if not word in stop_words]
    filtered_text = (" ").join(tokens_without_stopwords)
    return filtered_text


def calculate_sentiment_score(message):
    vs = vader_analyzer.polarity_scores(message)
    return vs

def calculate_emotion(vs):
    if not vs['neg'] > 0.1 and vs['pos'] - vs['neg'] > 0.5:
            return "POSITIVE"
    if not vs['pos'] > 0.1 and vs['pos'] - vs['neg'] <= -0.5:
            return "NEGATIVE"
    else:
        return "NEUTRAL"

slack_events_adapter.start(port=3000)
