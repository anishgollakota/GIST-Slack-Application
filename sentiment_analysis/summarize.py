from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from extractive import summarize
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

vader_analyzer = SentimentIntensityAnalyzer()

messages = {}

@slack_events_adapter.on("message")
def handle_message(event_data):
    global messages
    message = event_data["event"]
    channel = message["channel"]
    user = "<@%s>" % message["user"]
    text = message.get('text')
    tokens = text.split(' ')
    print(tokens)
    print()
    reference_user = ""
    if len(tokens) > 2:
        reference_user = tokens[2]
    if user in messages.keys():
        messages[user] += text
    else:
        messages[user] = text
    send_message = ""
    reference_message = ""
    if message.get("subtype") is None and "BOT TEST" in message.get('text') and message["user"]!="U0160T55TD2":
        send_message = "Responding to `BOT TEST` message sent by user <@%s>" % message["user"]
    if message.get("subtype") is None and tokens[1]=="summarize" and message["user"]!="U0160T55TD2":
        reference_message = messages[reference_user]
        send_message = summarize(reference_message)
        send_message += '\n'
        send_message += '\n'
        score, emotion = sentiment_analysis(reference_message)
        send_message += user + " seems " + emotion + " with a score of " + str(score)
        messages[reference_user] = ""
    slack_client.api_call("chat.postMessage", channel=channel, text=send_message)

def sentiment_analysis(reference_message):
    cleaned_text = ""
    cleaned_text = clean_text(reference_message)
    sentiment_score = calculate_sentiment_score(cleaned_text)
    emotion = calculate_emotion(sentiment_score)
    compound_score = sentiment_score['compound']
    print(compound_score)
    compound_emotion = calculate_compound_emotion(compound_score)
    return compound_score, compound_emotion

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

def calculate_compound_emotion(compound_score):
    if compound_score < -0.2:
        return "NEGATIVE"
    elif compound_score > 0.2:
        return "POSITIVE"
    else:
        return "NEUTRAL"

slack_events_adapter.start(port=3000)
