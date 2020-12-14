from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests


MAIN_URL = 'https://www.goodreads.com/review/list/13487053-ankit-modi?order=d&ref=nav_mybooks&shelf=read&sort=date_read&utf8=%E2%9C%93'
YEAR = '2019'


def get_html_using_selenium(url):
    # driver = webdriver.Chrome(executable_path='/Users/ankitmodi/Desktop/Code/goodreads_year_end_review/chromedriver')
    #
    # driver.get (MAIN_URL)
    # driver.find_element_by_id("userSignInFormEmail").send_keys("a.modi1422@gmail.com")
    # driver.find_element_by_id ("user_password").send_keys("a14a22a20a20")
    # # driver.find_element_by_id(“submit”).click()
    # # driver.find_element_by_xpath("//option[@value='Sign in']").click()
    # driver.find_element_by_xpath("//input[@type='submit' and @value='Sign in']").click()
    #
    # driver.get ("https://www.goodreads.com/review/list/13487053-ankit-modi?order=d&per_page=100&ref=nav_mybooks&shelf=read&sort=date_read&utf8=%E2%9C%93")
    # time.sleep(5)
    # driver.quit()



    # driver = webdriver.Chrome(executable_path='/Users/ankitmodi/Desktop/Code/goodreads_year_end_review/chromedriver')
    # driver.get (url)
    #
    # # handle infinite scroll
    # lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    # match = False
    # while(match==False):
    #     lastCount = lenOfPage
    #     time.sleep(3)
    #     lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    #     if lastCount==lenOfPage:
    #         match=True
    #
    # # Now that the page is fully scrolled, grab the source code.
    # my_html = driver.page_source
    # driver.quit()

    with open('tmp.html', 'r') as f:
        my_html = f.read()

    return my_html


def get_rating_from_text(rating_text):
    rating_dict = {'did not like it': '1',
                   'it was ok': '2',
                   'liked it': '3',
                   'really liked it': '4',
                   'it was amazing': '5'}

    return rating_dict[rating_text]


def get_books_data(soup):
    table = soup.find_all('table', {'id':'books'})[0]
    table_rows = table.find_all('tr')
    book_list = []

    for tr in table_rows[1:]:
        book_dict = {}

        # cover url
        td = tr.find_all('td', {'class':'field cover'})[0]
        img = td.find_all('img')[0]
        book_dict['cover_url'] = img['src']

        # parse title and book's url
        td = tr.find_all('td', {'class':'field title'})[0]
        a_link = td.find_all('a')[0]
        book_dict['title'] = a_link.get('title')
        book_dict['book_url'] = a_link.get('href')

        # author
        td = tr.find_all('td', {'class':'field author'})[0]
        a_link = td.find_all('a')[0]
        book_dict['author_name'] = a_link.text
        book_dict['author_url'] = a_link.get('href')

        # rating
        td = tr.find_all('td', {'class':'field rating'})[0]
        span = td.find_all('span', {'class':'staticStars notranslate'})[0]
        rating_text = span.get('title')
        rating = get_rating_from_text(rating_text)
        book_dict['rating'] = rating

        #review
        td = tr.find_all('td', {'class':'field review'})[0]
        span = td.find_all('span', {'style':'display:none'})[0]
        lines = [str(i) for i in span.contents]
        review = ' '.join(lines)
        book_dict['review'] = review



        book_list.append(book_dict)
        break
    return book_list



if __name__ == '__main__':
    html_str = get_html_using_selenium(MAIN_URL)

    # with open('tmp.html', 'w') as f:
    #     f.write(html_str)

    soup = BeautifulSoup(html_str, 'lxml')
    book_list = get_books_data(soup)
    print(book_list)



    # response = requests.get(MAIN_URL)
    # html_text = response.text
    # with open('tmp.html', 'w') as f:
    #     f.write(html_text)
