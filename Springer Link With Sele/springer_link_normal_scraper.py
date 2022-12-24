from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import numpy as np
import pandas as pd
import time
import os

### INPUTS

# Where to start searching
number_of_pages_start = 1
# what to search
what_to_search = "online sports betting"
# name of the file that stores de data
file_name = f"spring_link_information_starting_{number_of_pages_start}.xlsx"

###

path = os.getcwd().replace("\\", "/") + "/"

global_url = "https://link.springer.com"

## sleep from x and y seconds
x = 2
y = 4
##

formated_search = what_to_search.replace(" ", "+")

response = requests.get(f"https://link.springer.com/search/page/{number_of_pages_start}?query={formated_search}")
start_soup = BeautifulSoup(response.content,'lxml')
total_number_of_pages = int(start_soup.find("span", class_="number-of-pages").text)

## generating url for every page
pages_url = [f"https://link.springer.com/search/page/{n_page}?query={formated_search}" for n_page in range(number_of_pages_start, total_number_of_pages + 1)]
##

counter = 0
n_page = number_of_pages_start

information = {"article_type":[], 
                "title":[], 
                "link":[], 
                "abstract":[], 
                "author":[], 
                "date":[], 
                "year":[], 
                "n_citations":[]}

start = time.time()

for url in pages_url:

    browser = webdriver.Chrome("chromedriver.exe")
    browser.get(url)
    time.sleep( (y-x) * np.random.random() + y)
    soup = BeautifulSoup(browser.page_source,'lxml')
    mini_soup = soup.find("ol", class_ = "content-item-list")

    for article in mini_soup.find_all("li"):
        counter += 1

        try:
            ## article type
            article_type = article.find("p", class_ = "content-type").text.replace(" ","").replace("\n","")
            ##
        except Exception as e:
            article_type = np.nan

        try:
            ## title and link
            title_link = article.find("a", class_="title")
            full_link = global_url + title_link["href"]
            ##
            browser.get(full_link)
            time.sleep( (y-x) * np.random.random() + y)
            article_soup = BeautifulSoup(browser.page_source, 'lxml')
        except Exception as e:
            continue

        try:
            ### for open access
            ## authors
            try:
                authors = article_soup.find("ul", class_ = "c-article-author-list js-etal-collapsed js-no-scroll")
                author = ""
                for i in authors.find_all("li"):
                    author += i.find("a").text + ","
            except Exception as e:
                author = np.nan

            ## date
            try:
                date = article_soup.find("time")["datetime"]
            except Exception as e:
                date = np.nan
            ##

            ## abstract
            try:
                abstract = article_soup.find("div", class_ = "c-article-section__content").text
            except Exception as e:
                abstract = np.nan
            ##

            ## citations
            try:
                citations = article_soup.find_all("p", class_ = "c-article-metrics-bar__count")[1].text
                n_citations = [int(i) for i in citations.split() if i.isdigit()][0]
            except Exception as e:
                n_citations = np.nan

            # print("article_type", article_type)
            # print("title", title_link.text)
            # print("link", full_link)
            # print("author", author[:-1])
            # print("date", date)
            # print("year", date[:4])
            # print("abstract", abstract)
            # print("n_citations", n_citations)

            browser.refresh()

            information["article_type"].append(article_type)
            information["title"].append(title_link.text if title_link != np.nan else title_link)
            information["link"].append(full_link)
            information["abstract"].append(abstract)
            information["author"].append(author[:-1] if author != np.nan else author)
            information["date"].append(date)
            information["year"].append(int(date[:4]) if date != np.nan else date)
            information["n_citations"].append(n_citations)

        except Exception as e:
            ### for non open access
            ## authors
            try:
                authors = article_soup.find("ul", class_="test-contributor-names")
                author = ""
                for a in authors:
                    author += a.text + ","
            except Exception as e:
                author = np.nan
            ##

            ## date
            try:
                date = article_soup.find("time")["datetime"]
            except Exception as e:
                date = np.nan
            ##

            ## abstract
            try:
                abstract = article_soup.find("p", class_="Para").text
            except Exception as e:
                abstract = np.nan

            n_citations = np.nan

            # print("article_type", article_type)
            # print("title", title_link.text)
            # print("link", full_link)
            # print("author", author[:-1])
            # print("date", date)
            # print("year", date[:4])
            # print("abstract", abstract)
            # print("n_citations", n_citations)
            ###

            browser.refresh()

            information["article_type"].append(article_type)
            information["title"].append(title_link.text if title_link != np.nan else title_link)
            information["link"].append(full_link)
            information["abstract"].append(abstract)
            information["author"].append(author[:-1] if author != np.nan else author)
            information["date"].append(date)
            information["year"].append(int(date[:4]) if date != np.nan else date)
            information["n_citations"].append(n_citations)
        
        # print()
        # print("-----------------------------------------------------------------------------------------------")
        # print("Counter:", counter)

    browser.close()
    print(f"Page number {n_page} done")
    n_page += 1
    df = pd.DataFrame(information)
    df.to_excel(path + file_name)

try:
    browser.close()
except Exception as e:
    pass

print(df)
n_articles = df.shape[0]
print(f"\nScraped {n_articles} articles")

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)

print("Program runned for {:0>2}h:{:0>2}m:{:05.2f}s".format(int(hours), int(minutes), seconds))