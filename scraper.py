from selenium import webdriver
from selenium.webdriver.support import ui
import mysql.connector
import datetime
from mysql.connector import errorcode

def get_latest_news():
	results = []
	news_arr = []
	url = 'https://badmintonindonesia.org/app/information/default.aspx?'

	driver = webdriver.Firefox()

	driver.get(url)
    
	news_list = driver.find_elements_by_xpath('//div[@class="konten_dalem"]/div/ul[@class="berita_list"]/li')
	for news in news_list:
		news_detail = dict()
		news_detail['title'] = news.find_element_by_xpath('div/h3/a').text
		news_detail['preview'] = news.find_element_by_xpath('div/div[@class="lead"]').text
		news_detail['url'] = news.find_element_by_xpath('div/h3/a').get_attribute('href')
		news_arr.append(news_detail)

	for news in news_arr:
		result = dict()
		driver.get(news['url'])
		news_complete = driver.find_elements_by_xpath("//div[@class='berita_teks rich_text']")
		news_image = driver.find_elements_by_xpath("//div[@class='slideshow_didalam_details_inner']/div/img")
		news_author = driver.find_elements_by_xpath("//div[@class='meta_by']")
		news_published = driver.find_elements_by_xpath("//div[@class='meta_time']")[0].text
		news_published_arr = news_published.split('/')
		news_published_formated = news_published_arr[2] + '-' + news_published_arr[0] + '-' + news_published_arr[1]

		result['news_title'] = news['title']
		result['news_preview'] = news['preview']
		result['news_content'] = news_complete[0].text
		result['news_image'] = news_image[0].get_attribute("src")
		result['news_scraped'] = datetime.datetime.now()
		result['news_author'] = news_author[0].text
		result['news_published'] = datetime.datetime.strptime(news_published_formated, "%Y-%m-%d")
		results.append(result)
		
	driver.close()

	return results

def insert_news(data):
	print("Insert latest news to db")
	try:
		# open the database connection
		cnx = mysql.connector.connect(user='root', password='biteme10', host="127.0.0.1", database="ibadf")

		insert_sql = ("INSERT INTO news (news_title, news_preview, news_content, news_image, news_scraped, news_author, news_published) " +
		              "VALUES (%(news_title)s, %(news_preview)s, %(news_content)s, %(news_image)s, %(news_scraped)s, %(news_author)s, %(news_published)s)")

		# insert data to db
		cursor = cnx.cursor()
		cursor.executemany(insert_sql, data)

		# commit the new records
		cnx.commit()
		
		# close the cursor and connection
		cursor.close()
		cnx.close()

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		    print("Something is wrong with your user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
		    print("Database does not exist")
		else:
		    print(err)
	else:
		cnx.close()

news = get_latest_news()
# print(news)
# news = [{'news_title': 'bbbbb', 'news_preview': 'asdasdasd', 'news_content': 'asdasdad asdasd', 'news_image': 'ajpg', 'news_created': 'qqqqq', 'news_author': 'aaaaa'},{'news_title': 'bbbbb', 'news_preview': 'asdasdasd', 'news_content': 'asdasdad asdasd', 'news_image': 'ajpg', 'news_created': 'qqqqq', 'news_author': 'aaaaa'}];
insert_news(news)