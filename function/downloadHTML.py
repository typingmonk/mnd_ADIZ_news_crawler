from pathlib import Path
from function.reachDB import getDBConnect
from function.ROCEra import ROCE2CE
from psycopg2 import sql
import urllib.request as request
import bs4 as bs
# return value:
# 0 : 該網址被轉址、或是404
# 1 : 是貼文、而且是跟中共軍機進入防空識別區有關的貼文
# 2 : 是貼文但跟中共軍機進入防空識別區無關
def downloadHTML(pid):
	html_page = request.urlopen("https://www.mnd.gov.tw/Publish.aspx?p=" + str(pid)).read()
	soup = bs.BeautifulSoup(html_page, "html.parser")
	#確認是一則貼文，其餘可能是被轉址或錯誤頁面。
	if "thisPages" in str(soup):
		return getHTML(soup,pid)
	else:
		return 0

def getHTML(soup,pid):
	current_path = Path(__file__).parent.absolute()
	save_location = str(current_path.parent) + "/html/" + str(pid) + ".html"
	thisPages = soup.find_all("div", class_="thisPages")[0]
	thisPages_str = str(thisPages)

	if "軍機" in thisPages_str and "中共" in thisPages_str:
		#with open(save_location, 'w') as file:
		#	file.write(thisPages_str)
		save_TB_mnd_posts(pid, thisPages)
		save_TB_flight_records(pid, thisPages)
		return 1
	else:
		return 2

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
	title_zh_TW = p_soup[0].text.strip()

	#title_en_US
	title_en_US = p_soup[1].text.strip()

	#html
	html = str(soup)

	#reaction_zh_TW, reaction_en_US
	for i, p in enumerate(p_soup):
		if "應處作為" in p.text:
			reaction_zh_TW, reaction_en_US = p_soup[i+1].text.strip(), p_soup[i+2].text.strip()

	query = sql.SQL("""INSERT INTO mnd_posts
					   (post_id, post_date, post_url, title_zh_TW, title_en_US, html, reaction_zh_TW, reaction_en_US)
					   VALUES
					   ({a}, {b}, {c}, {d}, {e}, {f}, {g}, {h})""").format(
					a=sql.Literal(post_id),
					b=sql.Literal(post_date),
					c=sql.Literal(post_url),
					d=sql.Literal(title_zh_TW),
					e=sql.Literal(title_en_US),
					f=sql.Literal(html),
					g=sql.Literal(reaction_zh_TW),
					h=sql.Literal(reaction_en_US))

	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		conn.commit()
	conn.close()

def save_TB_aircraft_types(crafts, crafts_en):
	craft_ids = list()
	for i, craft in enumerate(crafts):
		#Check the type is in table or not.
		query = sql.SQL("SELECT craft_id FROM aircraft_types WHERE name_zh_TW = {a}").format(
						a=sql.Literal(craft))
		conn = getDBConnect()
		with conn.cursor() as cur:
			cur.execute(query)
			result = cur.fetchone()
			#if not, insert it into table.
			if result is None:
				query = sql.SQL("""INSERT INTO aircraft_types
								   (name_zh_TW, name_en_US) VALUES ({a}, {b}) RETURNING craft_id""").format(
								a=sql.Literal(crafts[i]),
								b=sql.Literal(crafts_en[i]))
				cur.execute(query)
				craft_id = cur.fetchone()[0]
				#print("new: ", craft_id)
				craft_ids.append(craft_id)
			else:
				#print("exists: ", result[0])
				craft_id = result[0]
				craft_ids.append(craft_id)
			conn.commit()
		conn.close()
	return craft_ids

def save_TB_flight_records(pid, soup):
	p_soup = soup.find_all("p")
	for i, p in enumerate(p_soup):
		if "二、" in p.text:
			s = i
		elif "三、" in p.text:
			e = i
			break
	p_soup = p_soup[s+1:e]
	p_texts = [p.text.strip() for p in p_soup]
	crafts, crafts_en  = p_texts[:int(len(p_texts)/2)], p_texts[int(len(p_texts)/2):]
	#print(crafts)
	#print(crafts_en)
	#print("target" , [c.split()[-1] for c in crafts])
	flight_cnts = list(map(get_digit, [c.split()[-1] for c in crafts]))
	flight_cnts = [cnt[0] for cnt in flight_cnts]
	crafts = [c.split()[0] for c in crafts]
	crafts_en = [c[c.find(" ")+1:] for c in crafts_en]
	#print(flight_cnts)
	#print(crafts)
	#print(crafts_en)
	craft_ids = save_TB_aircraft_types(crafts, crafts_en)
	for i, craft_id in enumerate(craft_ids):
		query = sql.SQL("""INSERT INTO flight_records (post_id, craft_id, craft_count)
						   VALUES ({a}, {b}, {c})""").format(
						a=sql.Literal(pid),
						b=sql.Literal(craft_id),
						c=sql.Literal(flight_cnts[i]))
		conn = getDBConnect()
		with conn.cursor() as cur:
			cur.execute(query)
			conn.commit()
		conn.close()

def get_digit(text):
	return list(filter(is_digit, text))

def is_digit(t):
	return t in ("0","1","2","3","4","5","6","7","8","9")

def format_post_date(date_raw):
	date_raw = date_raw.strip().replace("（","").replace("）","").replace("(","").replace(")","").replace(" ","")
	date_raw = date_raw.replace("星期一","")
	date_raw = date_raw.replace("星期二","")
	date_raw = date_raw.replace("星期三","")
	date_raw = date_raw.replace("星期四","")
	date_raw = date_raw.replace("星期五","")
	date_raw = date_raw.replace("星期六","")
	date_raw = date_raw.replace("星期七","")
	s = date_raw.find("中華民國")
	y = date_raw.find("年")
	m = date_raw.find("月")
	d = date_raw.find("日")
	return str(ROCE2CE(int(date_raw[s+4:y]))) + "-" + date_raw[y+1:m] + "-" + date_raw[m+1:d]
