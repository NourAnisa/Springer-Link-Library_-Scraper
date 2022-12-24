from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import pandas as pd
import time

### INPUTS

# what to search
what_to_search = ""
# name of the file that stores the data
file_name = what_to_search.replace(" ", "_") + "_articles.xlsx"

if what_to_search == "":
    print("Did not input the search topic")
    quit()

global_url = "https://link.springer.com"

## sleep from x and y seconds
x = 3
y = 5
##

information = {"article_type":[], 
                "title":[], 
                "link":[], 
                "abstract":[], 
                "author":[], 
                "date":[], 
                "year":[], 
                "n_citations":[],
                "discipline":[]}

formated_search = what_to_search.replace(" ", "+")

browser = webdriver.Chrome("chromedriver.exe")
browser.get(f'https://link.springer.com/search/page/1?facet-content-type="Article"&query="{formated_search}"')
time.sleep( (y-x) * np.random.random() + y)
see_all = browser.find_element_by_class_name("all").click()
time.sleep(2)

mini_soup = BeautifulSoup(browser.page_source,'lxml')

all_disciplines_box = mini_soup.find("div", id="colorbox")
all_disciplines_links = [global_url + link["href"] for link in all_disciplines_box.find_all("a", class_="facet-link")]
all_disciplines_names = [discipline.text for discipline in all_disciplines_box.find_all("span", class_="facet-title")]

if len(all_disciplines_links) != len(all_disciplines_names):
    print("Error with len of lists not matching")
    browser.close()
    quit()

start = time.time()
counter = 0

for discipline_index, discipline_link in enumerate(all_disciplines_links):
    browser.get(discipline_link)
    time.sleep(2)

    soup = BeautifulSoup(browser.page_source,'lxml')

    try:
        total_number_of_pages = int(soup.find("span", class_="number-of-pages").text.replace(",",""))
    except Exception as e:
        total_number_of_pages = 1

    splited_link = discipline_link.split("?")

    if total_number_of_pages != 1:
        pages_url = [splited_link[0] + "/page/" + str(n_page) + "?" + splited_link[1] for n_page in range(1, total_number_of_pages + 1)]
    else:
        pages_url = [discipline_link]

    print("Starting " + all_disciplines_names[discipline_index])

    for n_page, url in enumerate(pages_url):

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
                try:
                    information["author"].append(author[:-1] if author != np.nan else author)
                except Exception as e:
                    information["author"].append(np.nan)
                information["date"].append(date)
                information["year"].append(int(date[:4]) if date != np.nan else date)
                information["n_citations"].append(n_citations)
                information["discipline"].append(all_disciplines_names[discipline_index])

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
                try:
                    information["author"].append(author[:-1] if author != np.nan else author)
                except Exception as e:
                    information["author"].append(np.nan)
                information["date"].append(date)
                information["year"].append(int(date[:4]) if date != np.nan else date)
                information["n_citations"].append(n_citations)
                information["discipline"].append(all_disciplines_names[discipline_index])
            
            # print()
            # print("-----------------------------------------------------------------------------------------------")
            # print("Counter:", counter)

        print(f"Page number {n_page + 1} done")
        df = pd.DataFrame(information)
        df.to_excel(file_name)
        
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