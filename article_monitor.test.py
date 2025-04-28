# https://www.newsnow.co.uk/h/Technology/Cyber+Security/Cyber+Attacks?type=ln

import requests
from bs4 import BeautifulSoup
import time
import datetime

# get elements with the "article" class
def get_articles():
    url = 'https://www.newsnow.co.uk/h/Technology/Cyber+Security/Cyber+Attacks?type=ln'
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"})
    #print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(response.text)
    articles = soup.find_all('article')
    return articles


# get the title and link of each article
def get_article_info(articles):
    article_info = []
    #print(articles)
    for article in articles:
        title = article.find('a').text
        link = article.find('a')['href']
        # the timestamp is in a span element inside the class="article-publisher__timestamp" parameter
        # eg: <span data-timestamp="1728408883" class="article-publisher__timestamp" data-v-f47d8420="">18:34</span> where 1728408883 is the timestamp
        time = article.find('span', class_='article-publisher__timestamp')['data-timestamp']
        #print(time)
        article_info.append({'title': title, 'link': link, 'time': time})
    return article_info


# print the title and link of each article
def print_articles(article_info):
    for article in article_info:
        print(article['title'])
        print(article['link'])
        # convert time do datetime
        timestamp = int(article['time'])
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        print(dt_object)
        print()


# continuously check for new articles
def monitor_articles():
    articles = get_articles()
    article_info = get_article_info(articles)
    print_articles(article_info)
    print("-" * 50)
    while True:
        time.sleep(60)
        new_articles = get_articles()
        new_article_info = get_article_info(new_articles)
        for article in new_article_info:
            if article not in article_info:
                print(article['title'])
                print(article['link'])
                print()
        article_info = new_article_info


monitor_articles()

