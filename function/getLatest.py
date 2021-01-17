from function.reachDB import getDBConnect
from function.ROCEra import ROCE2CE
from pathlib import Path
from urllib.parse import quote
import urllib.request as request
import bs4 as bs

def getLatest():
	latest_DB_id , latest_DB_date = getDBLastestPost()
	latest_date = getLastestDate()
	if latest_date > latest_DB_date:
		return (latest_DB_id + 1, latest_date)
	else:
		return None
	

def getLastestDate():
	list_page_url = "https://www.mnd.gov.tw/PublishTable.aspx?Types=" + quote("即時軍事動態")
	post_list_page = request.urlopen(list_page_url)
	soup = bs.BeautifulSoup(post_list_page, "html.parser")
	latest_date = soup.find("td", class_="w-10").text
	latest_date = latest_date.split("/")
	CE = ROCE2CE(int(latest_date[0]))
	latest_date = str(CE) + "-" + latest_date[1] + "-" + latest_date[2]
	return latest_date

def getDBLastestPost():
	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute("""SELECT post_id, post_date
				     FROM mnd_posts
				     WHERE post_id = (SELECT MAX(post_id) FROM mnd_posts);""")
		result = cur.fetchone()
	conn.close()
	if result is None:
		return (77444, "2020-10-08")
	else:
		return (result[0], result[1].strftime("%Y-%m-%d"))
