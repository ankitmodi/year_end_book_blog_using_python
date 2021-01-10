from selenium import webdriver
import time
from bs4 import BeautifulSoup


YEAR = '2020'
OUTPUT_MD_FILE_PATH = 'markdown_file.md'
INTRO_PARA_OF_BLOG = f'{YEAR} was a good reading year for me. The Covid induced work-from-home saved ample travel hours for me to fall in love with reading again. Here are the books that I read this year - some of them were delightful; others not so much.\n'
CHROME_DRIVER_PATH = '/Users/ankitmodi/Desktop/Code/scraping_goodreads_using_python/chromedriver'
MAIN_URL = 'https://www.goodreads.com/review/list/13487053-ankit-modi?order=d&ref=nav_mybooks&shelf=read&sort=date_read&utf8=%E2%9C%93'


def get_html_using_selenium(url, CHROME_DRIVER_PATH):

    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
    driver.get (url)

    # handle infinite scroll
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True

    # Page is fully scrolled now. Next step is to extract the source code from it.
    my_html = driver.page_source
    driver.quit()

    # with open('tmp.html', 'r') as f:
    #     my_html = f.read()

    return my_html


def get_rating_from_text(rating_text):
    rating_dict = {'did not like it': '1',
                   'it was ok': '2',
                   'liked it': '3',
                   'really liked it': '4',
                   'it was amazing': '5'}

    return rating_dict[rating_text]


def get_books_data(html_str):
    soup = BeautifulSoup(html_str, 'lxml')

    table = soup.find_all('table', {'id':'books'})[0]
    table_rows = table.find_all('tr')
    book_list = []

    for tr in table_rows[1:]:
        book_dict = {}

        # parse cover_url
        td = tr.find_all('td', {'class':'field cover'})[0]
        img = td.find_all('img')[0]
        book_dict['cover_url'] = img['src']

        # parse title and book's url
        td = tr.find_all('td', {'class':'field title'})[0]
        a_link = td.find_all('a')[0]
        book_dict['title'] = a_link.get('title')
        book_dict['book_url'] = a_link.get('href')

        # parse author and author_url
        td = tr.find_all('td', {'class':'field author'})[0]
        a_link = td.find_all('a')[0]
        book_dict['author_name'] = a_link.text
        book_dict['author_url'] = a_link.get('href')

        # parse rating
        td = tr.find_all('td', {'class':'field rating'})[0]
        span = td.find_all('span', {'class':'staticStars notranslate'})[0]
        rating_text = span.get('title')
        rating = get_rating_from_text(rating_text)
        book_dict['rating'] = rating

        # parse review
        review = ''
        td = tr.find_all('td', {'class':'field review'})
        if(len(td) > 0):
            td = td[0]
            span = td.find_all('span')
            if(len(span) > 0):
                span = span[-1]
                lines = [str(i) for i in span.contents]
                review = ' '.join(lines)
        book_dict['review'] = review

        # parse date_read
        td = tr.find_all('td', {'class':'field date_read'})[0]
        span = td.find_all('span', {'class':'date_read_value'})[0]
        date_read = span.text
        book_dict['date_read'] = date_read

        book_list.append(book_dict)
        # break

    return book_list


def filter_and_sort_books(book_list, year):
    filtered_list = [i for i in book_list if year in i['date_read']]
    sorted_list = sorted(filtered_list, key=lambda k: k['rating'], reverse=True)
    return sorted_list


def create_markdown(filtered_and_sorted_book_list, year, intro_para,
                    md_file_path):
    url_prefix = 'https://www.goodreads.com/'

    with open(md_file_path, 'w') as f:
        f.write('---\n')
        f.write('layout: post\n')
        f.write(f'title: My Year in Books - {year}\n')
        # f.write(f'excerpt: {year} was a good year in terms of reading\n')
        f.write('---\n')
        f.write(f'{intro_para}\n')

        # loop over book list and create md paragraphs for each book
        for i in range(len(filtered_and_sorted_book_list)):
            curr_book = filtered_and_sorted_book_list[i]

            # title, book_url
            book_url = url_prefix + curr_book['book_url']
            f.write(f"### <a href='{book_url}' target='_blank'>{i+1}. {curr_book['title']}</a>\n")

            #cover_url
            small_cover_url = curr_book['cover_url']
            basename = small_cover_url.split('/')[-1]
            s = basename.index('._')
            e = basename.index('_.') + 1
            new_basename = basename[:s] + basename[e:]
            big_cover_url = small_cover_url.replace(basename, new_basename)
            f.write(f"![cover image]({big_cover_url})" + "{: height='300' width='200px' style='float:left; padding-right:20px; padding-bottom:5px; padding-top:5px' }\n")

            # author_name, author_url
            author_str = curr_book['author_name']
            author_arr = [i.strip() for i in author_str.split(',')]
            author_name = ' '.join(author_arr[::-1])
            author_url = url_prefix + curr_book['author_url']
            f.write(f"Author: <a href='{author_url}' target='_blank'>_{author_name}_</a>\n")
            f.write('<br>\n')

            # my rating
            f.write(f"My rating: ___{curr_book['rating']} out of 5 stars___\n")
            f.write('<br><br>\n')

            # review
            f.write(curr_book['review'] + '\n')
            f.write('<br clear="all"><br>\n\n\n\n')

    print('Markdown created !!')



if __name__ == '__main__':
    html_str = get_html_using_selenium(MAIN_URL, CHROME_DRIVER_PATH)

    book_list = get_books_data(html_str)

    filtered_and_sorted_book_list = filter_and_sort_books(book_list, YEAR)

    create_markdown(filtered_and_sorted_book_list, YEAR, INTRO_PARA_OF_BLOG,
                    OUTPUT_MD_FILE_PATH)
