import urllib.request, tempfile, io, bs4 as bs, string, random
from function.ROCEra import ROCE2CE
from function.reachDB import getDBConnect
from function.reachAWS_S3 import upload_fileobj_S3
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
	origin_filename = a_tag_pdf.text
	url = a_tag_pdf['href']
	s, e = url.find("/"), url.rfind("&")
	url = mnd_prefix + url[s+1:e]
	pdf_bytes = urllib.request.urlopen(url).read()

	# Extract map into .jpg
	img_jpg = convert_from_bytes(pdf_bytes, dpi=200, fmt="jpg", first_page=2, last_page=2, size=(960, None))[0]
	img_width, img_height = img_jpg.size

	in_mem_jpg = io.BytesIO()
	img_jpg.save(in_mem_jpg, format=img_jpg.format)
	in_mem_jpg.seek(0)
	#page.save("img/" + str(pid) + ".map.jpg", "JPEG")	

	# Extract text from pdf
	temp_pdf = tempfile.TemporaryFile()
	temp_pdf.write(pdf_bytes)
	text = extract_text(temp_pdf)
	lines = text.splitlines()
	time_raw = [line.strip().replace(" ","") for line in lines if line.strip() != ""][0]
	time = format_time(time_raw)
	temp_pdf.close()

	# Update post_timestamp
	query = sql.SQL("UPDATE mnd_posts SET post_timestamp = {a} WHERE post_id = {b}").format(
					a=sql.Literal(time),
					b=sql.Literal(pid))

	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		conn.commit()
	conn.close()

	# Insert pdf file information
	query = sql.SQL("""INSERT INTO files (filename_extension, post_id, origin_url, origin_filename) 
					   VALUES ({a}, {b}, {c}, {d}) """).format(
					a=sql.Literal(".pdf"),
					b=sql.Literal(pid),
					c=sql.Literal(unquote(url)),
					d=sql.Literal(origin_filename))

	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		conn.commit()
	conn.close()

	# Insert map img file information
	query = sql.SQL("""INSERT INTO files (filename_extension, post_id, origin_url, origin_filename)
					   VALUES ({a}, {b}, {c}, {d}) RETURNING file_id""").format(
					a=sql.Literal(".map.jpg"),
					b=sql.Literal(pid),
					c=sql.Literal(unquote(url)),
					d=sql.Literal(origin_filename))

	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		file_id = cur.fetchone()[0]
		conn.commit()
	conn.close()

	# Generate unique and random filename for upload to AWS S3
	not_unique = True
	while not_unique:
		s3_filename = random_string(48)
		query = sql.SQL("SELECT archive_id FROM aws_s3_archives WHERE object_url LIKE {a}").format(
				     	a=sql.Literal("%" + s3_filename + "%"))
		conn = getDBConnect()
		with conn.cursor() as cur:
			cur.execute(query)
			not_unique = len(cur.fetchall()) != 0
		conn.close()

	# Upload file to AWS S3
	object_url = upload_fileobj_S3(in_mem_jpg, s3_filename, ".jpg")

	# Insert AWS S3 storage information
	query = sql.SQL("""INSERT INTO aws_s3_archives (file_id, object_url, img_width, img_height)
					   VALUES ({a}, {b}, {c}, {d})""").format(
					a=sql.Literal(file_id),
					b=sql.Literal(object_url),
					c=sql.Literal(img_width),
					d=sql.Literal(img_height))

	conn = getDBConnect()
	with conn.cursor() as cur:
		cur.execute(query)
		conn.commit()
	conn.close()
	
	return "OK."

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
	if len(time) == 2:
		time += "00"
	return year + "-" + month + "-" + day + " " + time

def find_ascii(text):
	for i, t in enumerate(text):
		if ord(t) < 128:
			return i
	return -1

def random_string(length):
	allowed = string.ascii_letters + string.digits
	randomstring = ''.join([allowed[random.randint(0, len(allowed) - 1)] for x in range(length)])
	return randomstring
