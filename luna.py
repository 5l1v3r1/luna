
from time import sleep
from datetime import timedelta, date
import requests
from statistics import mean

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
"milbull" : "\033[102m\033[1mMildly bullish\033[0m", 
"modbull" : "\033[102m\033[1mModerately bullish\033[0m",
"verbull" : "\033[42m\033[1m\033[5mVery bullish\033[0m",
"milbear" : "\033[43m\033[1mMildly bearish\033[0m",
"modbear" : "\033[41m\033[1mModerately bearish\033[0m",
"verbear" : "\033[101m\033[1m\033[5mVery bearish\033[0m",
"neutral" : "\033[104m\033[1mNeutral\033[0m"
}

dates = []
sid = SentimentIntensityAnalyzer()

#zacks.com only produces tiny snippets of text and it's usually polluted with default text/self-advertisement, so i'm just cutting everything out right now 
def blacklist(text): 
    if "Please make sure your browser supports JavaScript and cookies" in text: 
        return True 
    if "zacks.com" in text: 
        return True
    else: 
        return False

def determine(score): 
    positive = 0.5
    negative = -0.5
    if (score > 0) and (score < (positive/2)):
        return "milbull"
    elif (score > 0) and (score > (positive/2)):
        return "modbull"
    elif (score >= positive): 
        return "verbull"
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
    news_urls = ["https://news.google.com/news/rss/search/section/q/${}+news?ned=us&gl=US&hl=en", "https://feeds.finance.yahoo.com/rss/2.0/headline?s={}&region=US&lang=en-US"]
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
            if blacklist(news.link.text) == True:
                pass 
            else:  
                links.append(news.link.text)
        total_links = total_links + links
    # removes duplicate URLs
    total_links = list(set(total_links))
    return total_links 

def get_content(link):
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
        print(link)
        print("\033[101m\033[1m\033[!] Download failed\033[0m")
        return None 
    else:
        article.parse()
        article.nlp()
        if len(article.text) < 200: #too short?
            keys = ''.join(article.keywords) #use extracted keywords for analysis instead
            return keys 
        else:
            print(link)
            print(article.publish_date)
            print("="*80)
            return article.text

def get_content_dates(link):
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
        print(link)
        print("\033[101m\033[1m\033[!] Download failed\033[0m")
        return None 
    else:
        article.parse()
        article.nlp()
        if (str(article.publish_date).split(" "))[0] not in dates:
            print(link)
            print("not in dates")
            return None 
        else: 
            if len(article.text) < 200: #too short?
                keys = ''.join(article.keywords) #use extracted keywords for analysis instead
                return keys 
            else:
                print(link)
                print(article.publish_date)
                print("="*80)
                return article.text


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
        data = pool.map(get_content, links)
        pool.close()
        pool.join()
    print(data)
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
    print("[!] Updating VADER lexicon...")
    sid.lexicon.update(words)
    ticker = sys.argv[1]
    links = fetch_urls(ticker)
    data = get_text(links)
    data = list(filter(None, data))
    compound_scores = []
    for text in data:
        if blacklist(text) == True: 
            pass
        else:  
            compound = analyze(text)
            compound_scores.append(compound)
            print("ARTICLE ANALYZED: ")
            print("\033[1mSCORE: " + str(compound) + " " + defs[determine(compound)] + "\033[0m" + "\n")
            print("="*50)
    print("\033[1mCOMPOUND POLARITY AVERAGE: " + "\033[104m\033[5m\033[1m" + str(mean(compound_scores)) + "\033[0m")
    print("\033[1mCURRENT MARKET SENTIMENT: " + defs[determine(mean(compound_scores))] + "\n")
    exit()
main()

