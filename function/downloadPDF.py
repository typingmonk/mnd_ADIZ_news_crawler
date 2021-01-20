import urllib.request
import bs4 as bs
import tempfile
from function.ROCEra import ROCE2CE
from function.reachDB import getDBConnect
from pdf2image import convert_from_bytes
from pdfminer.high_level import extract_text
from psycopg2 import sql
from urllib.parse import unquote
from PIL import Image

mnd_prefix = "https://www.mnd.gov.tw/NewUpload/"

def downloadPDF(pid):
	query = "SELECT html FROM mnd_posts WHERE post_id = " + str(pid)
	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		html = cur.fetchone()[0]
	conn.close()

	soup = bs.BeautifulSoup(html, 'html.parser')
	a_tags = soup.find_all('a', href=True)
	a_tag_pdf = [a for a in a_tags if ".pdf" in a['href']][0]
	filename = a_tag_pdf.text
	url = a_tag_pdf['href']
	s, e = url.find("/"), url.rfind("&")
	url = mnd_prefix + url[s+1:e]
	pdf_bytes = urllib.request.urlopen(url).read()

	# Extract map into .jpg
	page = convert_from_bytes(pdf_bytes, dpi=200, first_page=2, last_page=2, size=(960, None))[0]
	img_width, img_height = page.size
	#page.save("img/" + str(pid) + ".map.jpg", "JPEG")	

	# Extract text from pdf
	temp_pdf = tempfile.TemporaryFile()
	temp_pdf.write(pdf_bytes)
	text = extract_text(temp_pdf)
	lines = text.splitlines()
	time_raw = [line.strip().replace(" ","") for line in lines if line.strip() != ""][0]
	time = format_time(time_raw)

	# Update post_timestamp
	query = sql.SQL("UPDATE mnd_posts SET post_timestamp = {a} WHERE post_id = {b}").format(
					a=sql.Literal(time),
					b=sql.Literal(pid))

	# Insert pdf file information
	query = sql.SQL("""INSERT INTO files (filename_extension, post_id, origin_url, origin_filename) 
					   VALUES ({a}, {b}, {c}, {d}) """).format(
					a=sql.Literal(".pdf"),
					b=sql.Literal(pid),
					c=sql.Literal(unquote(url)),
					d=sql.Literal(filename))

	# Insert map img file information
	query = sql.SQL("INSERT INTO files (filename_extension, post_id) VALUES ({a}, {b}) RETURNING file_id").format(
					a=sql.Literal(".map.jpg"), b=sql.Literal(pid))

	# Insert AWS S3 storage information
	query = sql.SQL("""INSERT INTO aws_S3_archives (file_id, object_url, img_width, img_height)
					   VALUES ({a}, {b}, {c}, {d})""").format(
					a=sql.Literal("???"),
					b=sql.Literal("???"),
					c=sql.Literal(img_width),
					d=sql.Literal(img_height))

def format_time(time_raw):
	s = find_ascii(time_raw)
	y = time_raw.find("年")
	m = time_raw.find("月")
	d = time_raw.find("日")
	t = time_raw.rfind("時")
	year  = str(ROCE2CE(int(time_raw[s:y])))
	month = time_raw[y+1:m]
	day   = time_raw[m+1:d]
	time  = time_raw[d+1:t]
	return year + "-" + month + "-" + day + " " + time

def find_ascii(text):
	for i, t in enumerate(text):
		if ord(t) < 128:
			return i
	return -1
