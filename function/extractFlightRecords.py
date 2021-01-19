from function.reachDB import getDBConnect
from psycopg2 import sql
import bs4 as bs

# return 0: Done
# return 1: find no post in table `mnd_posts`
 
def save_TB_flight_records(pid):

	query = sql.SQL("SELECT html FROM mnd_posts WHERE post_id = {a}").format(a=sql.Literal(pid))
	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		result = cur.fetchone()
		html = result[0]
		soup = bs.BeautifulSoup(result[0], "html.parser")
	conn.close()

	p_soup = soup.find_all("p")
	for i, p in enumerate(p_soup):
		if "二、" in p.text:
			s = i
		elif "三、" in p.text:
			e = i
			break
	p_soup = p_soup[s+1:e]
	p_texts = [p.text.strip() for p in p_soup]

	mode = check_record_mode(p_texts)
	if mode == 0:
		flight_cnts, crafts, crafts_en = extract_records_mode0(p_texts)
	elif mode == 1:
		flight_cnts, crafts, crafts_en = extract_records_mode1(p_texts)
	elif mode == 2:
		flight_cnts, crafts, crafts_en = extract_records_mode2(p_texts)
	

	# "運-8" 改成 "運8" 避免被認為是不同的機型
	crafts = [c.replace("-","") for c in crafts]
	name_ids = save_TB_aircraft_names(crafts, crafts_en)

	for i, name_id in enumerate(name_ids):
		query = sql.SQL("""INSERT INTO flight_records (post_id, name_id, craft_count)
						   VALUES ({a}, {b}, {c})""").format(
						a=sql.Literal(pid),
						b=sql.Literal(name_id),
						c=sql.Literal(flight_cnts[i]))
		conn = getDBConnect()
		with conn.cursor() as cur:
			cur.execute(query)
			conn.commit()
		conn.close()

def check_record_mode(p_texts):
	if p_texts[0].find("(") > -1 or p_texts[0].find("（") > -1 or len(p_texts) == 1:
		return 0
	text = p_texts[1]
	if all(ord(t) < 128 for t in text):
		return 1
	else:
		return 2
	
#
#  post_id = 77588
#  Mode0 example:
# 運-8反潛機 1架次(One Y-8 ASW)
# 運-8遠干機 1架次(One Y-8 EW)
#
def extract_records_mode0(p_texts):
	crafts, crafts_en = list(), list()
	for p_text in p_texts:
		p_text = p_text.replace("（","(").replace("（",")")
		i = p_text.find("(")
		crafts.append(p_text[:i])
		crafts_en.append(p_text[i+1:-1])
	flight_cnts = list(map(get_digit, [c.split()[-1] for c in crafts]))
	flight_cnts = [cnt[0] for cnt in flight_cnts]
	crafts = [c.split()[0] for c in crafts]
	crafts_en = [c[c.find(" ")+1:] for c in crafts_en]
	return flight_cnts, crafts, crafts_en 

#
#  post_id = 77447
#  Mode1 example:
# 運8型機  1架次
# One Y-8
# 運9型機  1架次
# One Y-9
#
def extract_records_mode1(p_texts):
	crafts    = [p_text for i, p_text in enumerate(p_texts) if i % 2 == 0]
	crafts_en = [p_text for i, p_text in enumerate(p_texts) if i % 2 == 1]
	flight_cnts = list(map(get_digit, [c.split()[-1] for c in crafts]))
	flight_cnts = [cnt[0] for cnt in flight_cnts]
	crafts = [c.split()[0] for c in crafts]
	crafts_en = [c[c.find(" ")+1:] for c in crafts_en]
	return flight_cnts, crafts, crafts_en

#
#  post_id = 77497
#  Mode2 example:
# 運8電偵機  1架次
# 運8遠干機  1架次
# One Y-8 ELINT
# One Y-8 EW
#
def extract_records_mode2(p_texts):
	crafts, crafts_en  = p_texts[:int(len(p_texts)/2)], p_texts[int(len(p_texts)/2):]
	flight_cnts = list(map(get_digit, [c.split()[-1] for c in crafts]))
	flight_cnts = [cnt[0] for cnt in flight_cnts]
	crafts = [c.split()[0] for c in crafts]
	crafts_en = [c[c.find(" ")+1:] for c in crafts_en]
	return flight_cnts, crafts, crafts_en

def save_TB_aircraft_names(crafts, crafts_en):
	name_ids = list()
	for i, craft in enumerate(crafts):
		#Check the type is in table or not.
		query = sql.SQL("SELECT name_id FROM aircraft_names WHERE name_zh_TW = {a}").format(
						a=sql.Literal(craft))
		conn = getDBConnect()
		with conn.cursor() as cur:
			cur.execute(query)
			result = cur.fetchone()
			#if not, insert it into table.
			if result is None:
				query = sql.SQL("""INSERT INTO aircraft_names
								   (name_zh_TW, name_en_US) VALUES ({a}, {b}) RETURNING name_id""").format(
								a=sql.Literal(crafts[i]),
								b=sql.Literal(crafts_en[i]))
				cur.execute(query)
				name_id = cur.fetchone()[0]
				#print("new: ", name_id)
				name_ids.append(name_id)
			else:
				#print("exists: ", result[0])
				name_id = result[0]
				name_ids.append(name_id)
			conn.commit()
		conn.close()
	return name_ids

def get_digit(text):
	return list(filter(is_digit, text))

def is_digit(t):
	return t in ("0","1","2","3","4","5","6","7","8","9")
