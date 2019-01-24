luna
====
[![Build Status](https://travis-ci.com/blacchat/luna.svg?branch=master)](https://github.com/blacchat/luna)
[![Starred](https://img.shields.io/github/stars/blacchat/luna.svg)](https://github.com/blacchat/luna)


Financial news sentiment analysis tool<br/>

requirements
============
* [newspaper3k](https://github.com/codelucas/newspaper])
* [nltk]([https://www.nltk.org/)
* [vader and vader lexicon](https://www.nltk.org/_modules/nltk/sentiment/vader.html)
* [bs4](https://pypi.org/project/beautifulsoup4/)

### usage
```
[satoshi@blockchain luna]$ python luna.py TLRY
 (                                     
 )\   (             )            (     
((_) ))\   (     ( /(     `  )   )\ )  
 _  /((_)  )\ )  )(_))    /(/(  (()/(  
| |(_))(  _(_/( ((_)_    ((_)_\  )(_)) 
| || || || ' \))/ _` | _ | '_ \)| || | 
|_| \_,_||_||_| \__,_|(_)| .__/  \_, | 
                         |_|     |__/
    
200 potential links found for this ticker.
Would you like to set a date range? [Y/N]
N

================================================================================
https://globenewswire.com/news-release/2018/12/11/1665107/0/en/Ready-Set-Grow-A-New-Era-with-2018-Farm-Bill-Cronos-Group-Inc-Canopy-Growth-Corporation-Tilray-Inc-Cannabis-Sativa-Inc-American-Premium-Water-Corporation.html
Ready, Set, Grow – A New Era with 2018 Farm Bill; Cronos Group Inc., Canopy Growth Corporation, Tilray, Inc., Cannabis Sativa, Inc., American Premium Water Corporation
2018-12-11 00:00:00
================================================================================
https://seekingalpha.com/article/4227434-get-lockup-expires-tilray-strong-sell-50-percent-downside
Get Out Before The Lockup Expires: Tilray Is A Strong Sell With 50% Downside
2018-12-11 11:30:06+00:00
================================================================================
https://www.fool.ca/2018/12/12/is-this-the-end-for-marijuana-stocks/
Is This the End for Marijuana Stocks?
2018-12-12 00:00:00
================================================================================
https://postanalyst.com/2018/12/10/the-long-term-viability-of-tilray-inc-tlry-hasbro-inc-has/
The long-Term Viability Of Tilray, Inc. (TLRY), Hasbro, Inc. (HAS)
2018-12-10 00:00:00
================================================================================
https://finance.yahoo.com/news/4-reasons-why-pot-stocks-171629606.html?.tsrc=rss
4 Reasons Why Pot Stocks Will Be More Stable In 2019
2018-12-10 17:16:29+00:00
================================================================================

......

Analyzing text..
ARTICLE ANALYZED: 
SCORE: 0.104232 Very mildly bullish

==================================================
Analyzing text..
ARTICLE ANALYZED: 
SCORE: 0.12189661016949152 Very mildly bullish

==================================================
Analyzing text..
ARTICLE ANALYZED: 
SCORE: 0.2564266666666667 Moderately bullish

==================================================
Analyzing text..
ARTICLE ANALYZED: 
SCORE: 0.1712074074074074 Mildly bullish

==================================================
Analyzing text..
ARTICLE ANALYZED: 
SCORE: -0.013025000000000004 Mildly bearish

==================================================
Analyzing text..
ARTICLE ANALYZED: 
SCORE: 0.14577777777777778 Mildly bullish

==================================================
Analyzing text..
ARTICLE ANALYZED: 
SCORE: 0.19149615384615384 Mildly bullish

==================================================
200 links analyzed.
TOP 10 KEYWORDS: tilray tlry stock company price shares cannabis stocks market average
COMPOUND POLARITY AVERAGE: 0.16357265947092867
CURRENT MARKET SENTIMENT: Mildly bullish

```

## upcoming (near future)
* Contextual polarity extraction for better accuracy
* Better support for different exchanges, eg Euronext, HKEX, SZE, JPX etc.
* Integration with SeekingAlpha to allow more data to be analyzed
* ~~Removal of irrelevant articles (low priority)~~

## to-do list (distant future)
* Clean up code 
* Remove urllib
* Improve accuracy of lexicon (might use Tensorflow)

### test.py
test.py tests the accuracy of the scores in luna_lexicon.py and the functionality of luna in general. Only takes individual URLs, not stock tickers. 

### luna_lexicon.py 
Contains a dictionary of positive and negative words in rough alphabetical order, which is used to supplement vader's own lexicon. luna_lexicon.py will **ONLY** contain words used in a financial context, eg. 'bearish' : -3.0, 'surge' : 3.0. Any other additions will be added to a different lexicon. 
## FAQ
### Why is luna giving me a rating of "bullish" when I search for a security that has recently dropped? 
There could be three reasons as to why this is the case: 
### 1. Insufficient data / incorrect timespan 
If $XOM is trading at 86.60 for 100 days and the market sentiment is bullish, a sudden sentiment reversal when the price drops to 4.21 on day 101 may not sufficiently outweigh the previous 100 days of glowing Seeking Alpha bullish spam posts to give an accurate result. I'm probably going to ~~add an option to give a start and end date for articles, and~~ introduce a 0-1 "relevance" scoring system where older news is assigned a lower score. 
### 2. Data pollution 
When newspaper3k grabs text from an article, it strips all tags, etc and returns the full text. Unfortunately, this occasionally includes irrelevant information that sometimes slants the final polarity score for the security. For example, in [this article](https://seekingalpha.com/article/4223459-nvidias-prospects-look-much-worse-hood?page=2) there is an unnecessary block of advertisement text at the bottom: 
> Subscribers to Beyond The Hype have access to all the linked articles that may otherwise be inaccessible. For timely, cutting-edge insights, analysis and investing ideas of solar, battery, autonomous vehicles, and other emerging technology stocks, check out Beyond the Hype. This Marketplace service gives you early access to my best investing ideas, along with event driven and arbitrage opportunities when they are most edgy and actionable. If you want expert advice on seeing through the hype, separating fact from fiction, avoiding investing landmines in emerging technologies, and an opportunity to participate in a vibrant and intellectually stimulating real-time chat room with other high-caliber, like-minded investors, consider subscribing to Beyond the Hype today. Subscribers also get access to all past articles.

Words like "high-caliber", "best", "timely", "cutting-edge", "intellectually" and "vibrant" bias the score towards positive even though the text is totally irrelevant to the topic. I could fix this by immediately chopping out all sentence tokens that do not pertain to the identified topic(s) of the text, but then I also run the risk of deleting relevant information. :-( 
### 3. Inaccurate lexicon 
VADER is built for analyzing social media, and its lexicon reflects that purpose. News outlets use much more mitigated language and a whole different set of vocabulary when compared to tweets: 
> FUCK $MU, micron is a fucking garbage fire, lost $45k on calls today" - @loser 4 retweets, 20 likes

> $MU dropped over %3.5 today following a disappointing earnings release." - Bloomberg

A good 50% of VADER's lexicon is most likely useless for financial sentiment analysis. Goldman Sachs does not use emoticons or capitalize words.

### Why is luna retrieving irrelevant results? 
Currently working on fixing this, will be adding more exclusively financial news RSS feeds soon. 

### i bought calls on AMD when luna said it was very bullish and now i have to remortgage my house and sell my car wtf??? im suing
lol 


## sources
https://people.cs.pitt.edu/~wiebe/pubs/papers/emnlp05polarity.pdf

https://pdfs.semanticscholar.org/b7e9/18806d84412e791a479eb7df05ed1b06ba76.pdf

https://www.aclweb.org/anthology/J/J09/J09-3003.pdf

http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf

https://researchgate.net/publication/283954600_Sentiment_Analysis_An_Overview_from_Linguistics

