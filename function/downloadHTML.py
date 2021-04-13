from pathlib import Path
from function.reachDB import getDBConnect
from function.ROCEra import ROCE2CE
from psycopg2 import sql
import urllib.request as request
import bs4 as bs
# return value:
# post_date : 是貼文、而且是跟中共軍機進入防空識別區有關的貼文
# None : 其他
def downloadHTML(pid):
	html_page = request.urlopen("https://www.mnd.gov.tw/Publish.aspx?p=" + str(pid)).read()
	soup = bs.BeautifulSoup(html_page, "html.parser")
	#確認是一則貼文，其餘可能是被轉址或錯誤頁面。
	if "thisPages" in str(soup):
		return getHTML(pid, soup)

def getHTML(pid, soup):
	current_path = Path(__file__).parent.absolute()
	save_location = str(current_path.parent) + "/html/" + str(pid) + ".html"
	thisPages = soup.find_all("div", class_="thisPages")[0]
	thisPages_str = str(thisPages)

	if ("媒體" not in thisPages_str) and ("軍機" in thisPages_str and "中共" in thisPages_str) or ("西南空域空情動態" in thisPages_str and ".csv" not in thisPages_str):
		#store at local
		#with open(save_location, 'w') as file:
		#	file.write(thisPages_str)
		return save_TB_mnd_posts(pid, thisPages)

def save_TB_mnd_posts(pid, soup):
	#post_id
	post_id = pid

	#post_date
	p_soup = soup.find_all("p")
	date_raw = [p.text for p in p_soup if "年" in p.text and "月" in p.text and "日" in p.text][0]
	post_date = format_post_date(date_raw)

	#post_url
	post_url = "https://www.mnd.gov.tw/Publish.aspx?p=" + str(pid)

	#title_zh_TW
	#title_zh_TW = p_soup[0].text.strip()

	#title_en_US
	#title_en_US = p_soup[1].text.strip()

	#html
	html = str(soup)

	#reaction_zh_TW, reaction_en_US
	#for i, p in enumerate(p_soup):
	#	if "應處作為" in p.text:
	#		reaction_zh_TW, reaction_en_US = p_soup[i+1].text.strip(), p_soup[i+2].text.strip()

	
	#query = sql.SQL("""INSERT INTO mnd_posts
	#				   (post_id, post_date, post_url, title_zh_TW, title_en_US, html, reaction_zh_TW, reaction_en_US)
	#				   VALUES
	#				   ({a}, {b}, {c}, {d}, {e}, {f}, {g}, {h})""").format(
	#				a=sql.Literal(post_id),
	#				b=sql.Literal(post_date),
	#				c=sql.Literal(post_url),
	#				d=sql.Literal(title_zh_TW),
	#				e=sql.Literal(title_en_US),
	#				f=sql.Literal(html),
	#				g=sql.Literal(reaction_zh_TW),
	#				h=sql.Literal(reaction_en_US))

	query = sql.SQL("""INSERT INTO mnd_posts
					   (post_id, post_date, post_url, html)
					   VALUES
					   ({a}, {b}, {c}, {d})
					   RETURNING post_date""").format(
					a=sql.Literal(post_id),
					b=sql.Literal(post_date),
					c=sql.Literal(post_url),
					d=sql.Literal(html))

	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		post_date = cur.fetchone()[0]
		conn.commit()
	conn.close()
	return post_date.strftime("%Y-%m-%d")

def format_post_date(date_raw):
	date_raw = date_raw.strip().replace("（","").replace("）","").replace("(","").replace(")","").replace(" ","")
	date_raw = date_raw.replace("星期一","")
	date_raw = date_raw.replace("星期二","")
	date_raw = date_raw.replace("星期三","")
	date_raw = date_raw.replace("星期四","")
	date_raw = date_raw.replace("星期五","")
	date_raw = date_raw.replace("星期六","")
	date_raw = date_raw.replace("星期七","")
	date_raw = date_raw[date_raw.find("中華民國"):]
	s = date_raw.find("中華民國")
	y = date_raw.find("年")
	m = date_raw.find("月")
	d = date_raw.find("日")
	return str(ROCE2CE(int(date_raw[s+4:y]))) + "-" + date_raw[y+1:m] + "-" + date_raw[m+1:d]
