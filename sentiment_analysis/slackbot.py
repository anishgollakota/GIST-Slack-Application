from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import json
import textblob
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


@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    channel = message["channel"]
    user = "<@%s>" % message["user"]
    message_text = clean_text(message.get('text'))
    sentiment_score = calculate_sentiment_score(message_text)
    emotion = calculate_emotion(sentiment_score)
    if message.get("subtype") is None and "BOT TEST" in message.get('text') and message["user"]!="U0160T55TD2":
        send_message = "Responding to `BOT TEST` message sent by user <@%s>" % message["user"]
    if message.get("subtype") is None and "hi" in message.get('text') and message["user"]!="U0160T55TD2":
        send_message = "Your sentiment score is " + str(sentiment("hi"))
    if message.get("subtype") is None and message["user"]!="U0160T55TD2":
        send_message = user + " seems " + emotion + ". Their sentiment score is " + str(sentiment_score)
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
    sentiment_score = TextBlob(message).sentiment.polarity
    return sentiment_score

def calculate_emotion(sentiment_score):
    if sentiment_score <= -0.8:
        return "VERY UNHAPPY"
    if sentiment_score <= -0.5:
        return "UNHAPPY"
    if sentiment_score <= -0.2:
        return "SLIGHTLY UNHAPPY"
    if sentiment_score <= 0.2:
        return "NEUTRAL"
    if sentiment_score <= 0.5:
        return "SLIGHTLY HAPPY"
    if sentiment_score <= 0.8:
        return "HAPPY"
    else:
        return "VERY HAPPY"

slack_events_adapter.start(port=3000)
