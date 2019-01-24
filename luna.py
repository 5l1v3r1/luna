
from utils.ticker import find_ticker
from collections import Counter

from time import sleep
from datetime import timedelta, date
import requests

from statistics import mean
import numpy as np 

import tkinter
import matplotlib.pyplot as plt

from newspaper import Article
from newspaper import Config
from newspaper import fulltext

from os import sys

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer  

from multiprocessing.dummy import Pool as ThreadPool

import luna_lexicon
words = luna_lexicon.additions

defs = {
"ver-milbull" : "\033[102m\033[1mVery mildly bullish\033[0m",
"milbull" : "\033[102m\033[1mMildly bullish\033[0m", 
"modbull" : "\033[102m\033[1mModerately bullish\033[0m",
"verbull" : "\033[42m\033[1m\033[5mVery bullish\033[0m",
"ver-milbear" : "\033[43m\033[1mMildly bearish\033[0m",
"milbear" : "\033[43m\033[1mMildly bearish\033[0m",
"modbear" : "\033[41m\033[1mModerately bearish\033[0m",
"verbear" : "\033[101m\033[1m\033[5mVery bearish\033[0m",
"neutral" : "\033[104m\033[1mNeutral\033[0m"
}

dates = []
keywords = []
ticker = ""
name = ""
sid = SentimentIntensityAnalyzer()

def determine(score): 
    positive = 0.5
    negative = -0.5
    if (score > 0) and (score < (positive/4)): 
        return "ver-milbull"
    elif (score > 0) and (score < (positive/2)):
        return "milbull"
    elif (score > 0) and (score > (positive/2)):
        return "modbull"
    elif (score >= positive): 
        return "verbull"
    elif (score < 0) and (score < (negative/4)): 
        return "ver-milbear"
    elif (score < 0) and (score > (negative/2)):
        return "milbear"
    elif (score < 0) and (score < (negative/2)): 
        return "modbear"
    elif (score <= negative): 
        return "verbear"
    else: 
        return "neutral"
    
def analyze(text): 
    global sid 
    print("Analyzing text..")
    tokenized = nltk.sent_tokenize(text)
    compound = [] 
    scores = [sid.polarity_scores(token) for token in tokenized]
    compound = [score["compound"] for score in scores]
    return mean(compound)


def fetch_urls(ticker):
    news_urls = ["https://news.google.com/news/rss/search/section/q/${}", "https://news.google.com/news/rss/search/section/q/${}+stocks", "https://feeds.finance.yahoo.com/rss/2.0/headline?s={}&region=US&lang=en-US"]
    total_links = []
    for news_url in news_urls: 
        news_url = news_url.format(ticker)
        Client=urlopen(news_url)
        xml_page=Client.read()
        Client.close()

        links = []
        soup_page=soup(xml_page,"xml")
        news_list=soup_page.findAll("item")
        for news in news_list:
            links.append(news.link.text)
        total_links = total_links + links
    # removes duplicate URLs
    total_links = list(set(total_links))
    return total_links 

def relevancy_check(link, title, keywords): 
    global ticker 
    global name 
    keywords = ' '.join(keywords)
    if name != None: 
        if name.lower() not in link and name.lower() not in keywords and name not in title: 
            if ticker not in link and ticker not in keywords and ticker not in title: 
                return False
            else: 
                return True 
        else: 
            return True
    else: 
        if ticker.lower() not in link and ticker.lower() not in keywords and ticker not in title: 
            return False
        else: 
            return True
def get_content(link):
    global keywords
    global dates 
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    config.memoize_articles = True 
    config.fetch_images = False 
    config.https_success_only = False
    article = Article(url=link, config=config)
    sleep(0.2)
    article.download() 
    if article.download_state == 1 : #has the download failed? eg. due to 403 
        print("\033[101m\033[1m\033[!] Download failed\033[0m")
        return None 
    else:
        article.parse()
        article.nlp()
        if relevancy_check(link, article.title, article.keywords) == False: 
            return None
        else:
            if len(article.text) < 200: #too short
                return None 
            else:
                print(link)
                print(article.title)
                print(article.publish_date)
                print("="*80)
                keywords = keywords + article.keywords
                return (article.text + "\n=====DATE:" + str(article.publish_date))

def get_content_dates(link):
    global keywords
    global dates 
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    config.memoize_articles = True 
    config.fetch_images = False 
    config.https_success_only = False

    article = Article(url=link, config=config)
    sleep(0.1)
    article.download() 
    if article.download_state == 1 : #has the download failed? eg. due to 403 
        print(link)
        print("\033[101m\033[1m\033[!] Download failed\033[0m")
        return None 
    else:
        article.parse()
        article.nlp()
        if (str(article.publish_date).split(" "))[0] not in dates:
            return None 
        else: 
            if relevancy_check(link, article.text, article.keywords) == False: 
                return None
            else:
                if len(article.text) < 200: #too short?
                    return None
                else:
                    print(link)
                    print(article.title)
                    print(article.publish_date)
                    print("="*80)
                    keywords = keywords + article.keywords
                    return (article.text + "\n=====DATE:" + str(article.publish_date))

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def get_text(links): 
    global dates
    data = []
    print("{} potential links found for this ticker.".format(len(links)))
    answer = input("Would you like to set a date range? [Y/N]\n")
    if answer == "N" or answer == "n":
        pass 
        pool = ThreadPool(4)
        data = pool.map(get_content, links)
        pool.close()
        pool.join()
    elif answer == "Y" or answer == "y": 
        print("Format: dd/mm/yyyy")
        startdate = input("Start at: ").split("/")
        enddate = input("End at: ").split("/")
        startday = int(startdate[0])
        endday = int(enddate[0])
        startmonth = int(startdate[1])
        endmonth = int(enddate[1])
        startyear = int(startdate[2])
        endyear = int(enddate[2])
        for dt in daterange(date(startyear, startmonth, startday), date(endyear, endmonth, endday)): 
            dates.append(dt.strftime("%Y-%m-%d"))
        pool = ThreadPool(4)
        data = pool.map(get_content_dates, links)
        pool.close()
        pool.join()
    else: 
        print("Answer must be Y or N.")
        exit()
    return data

def main(): 

    print("""\

 (                                     
 )\   (             )            (     
((_) ))\   (     ( /(     `  )   )\ )  
 _  /((_)  )\ )  )(_))    /(/(  (()/(  
| |(_))(  _(_/( ((_)_    ((_)_\  )(_)) 
| || || || ' \))/ _` | _ | '_ \)| || | 
|_| \_,_||_||_| \__,_|(_)| .__/  \_, | 
                         |_|     |__/
    """)
    global sid
    global keywords
    global name
    global ticker
    global dates
    print("Updating VADER lexicon...")
    sid.lexicon.update(words)
    if len(sys.argv) == 1: 
        print("Must supply ticker")
        exit()
    ticker = sys.argv[1]
    name = find_ticker(ticker)
    if name != None: 
        print(name)
    else: 
        print("Not found in list.")
    links = fetch_urls(ticker)
    data = get_text(links)
    data = list(filter(None, data))
    datastore = dict(zip(dates, [0 for x in range(0,len(dates))]))
    compound_scores = []
    for i in datastore: 
        datastore[i] = []
    for text in data:
        compound = analyze(text)
        if len(dates) != 0:
            textdate = (text.split("DATE:",1)[1]).split(" ")[0]
            compound_scores.append(compound)
            datastore[textdate].append(compound)
        else: 
            compound_scores.append(compound)
        print("Article analyzed. ")
        print("\033[1mSCORE: " + str(compound) + " " + defs[determine(compound)] + "\033[0m" + "\n")
        print("="*50)
    datastore = dict([(k,v) for k,v in datastore.items() if len(v) > 0])
    if len(dates) != 0:
        for i in datastore: 
            datastore[i] = mean(datastore[i])

    print("{} links analyzed.".format(len(compound_scores)))
    x = [word[0] for word in Counter(keywords).most_common(10)]
    print("Top 10 keywords: " + ' '.join(x))
    print("\033[1mCompound polarity average: " + "\033[104m\033[1m" + str(mean(compound_scores)) + "\033[0m")
    print("\033[1mVariance: " + str(np.var(compound_scores)))
    print("\033[1mMarket sentiment: " + defs[determine(mean(compound_scores))] + "\n")
    if len(dates) == 0:
        exit()
    else:
        print("Generating plot...")
        plt.rc('xtick', labelsize=8) # will make this automatically scale later
        lists = sorted(datastore.items())
        x, y = zip(*lists)
        plt.plot(x, y)
        answer = input("Show plot? [Y/N]\n")
        if answer == "y" or answer == "Y": 
            plt.show()
        else:
            exit()
main()
