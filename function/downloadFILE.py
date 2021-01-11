from pathlib import Path
import urllib.request
import bs4 as bs
from urllib.parse import quote, unquote

current_path = Path(__file__).parent.absolute()
root_path = str(current_path.parent)
img_dir = root_path + "/img/"
pdf_dir = root_path + "/pdf/"
mnd_prefix = "https://www.mnd.gov.tw/NewUpload"

def downloadFILE(pid):
	file_idx = 0
	html_file_location = root_path + "/html/" + str(pid) + ".html"
	with open(html_file_location, "r") as f:
		html_doc = f.read()
		soup = bs.BeautifulSoup(html_doc, 'html.parser')
		img_locations = list()
		pdf_locations = list()
		#確認文章中跟"中共"有關
		if "中共" not in str(soup):
			return (img_locations, pdf_locations)
		# 取得貼文中所有的 <a> tag 連結
		a_tags = soup.find_all('a', href=True)
		# 確認每一個 <a> tag 連結
		for a_tag in a_tags:
			file_href = unquote(a_tag['href'])
			# 將 href 根據 '/' 與 '&' 把連結切開，為了避免 find() 失敗有個 if 條件確認
			# 確認 href 中是有附檔名，用 '.' 確認
			if file_href.find('/') < 0 or file_href.find('&') < 0 or file_href.find('/') >= file_href.find('&'):
  				continue
			if file_href.find('.') < 0:
				continue
			file_extension = file_href[file_href.rindex('.'):file_href.index('&')].lower()
			file_postfix = file_href[file_href.index('/'):file_href.index('&')] 
			file_url = mnd_prefix + file_postfix
			# 下載的檔案分 pdf, img(other)
			# 如果未來有預期以外的檔案類型會被存成 img
			if "pdf" in file_href:
				save_at = pdf_dir + str(pid) + "_" + str(file_idx) + file_extension
				pdf_locations.append(save_at)
			else:
				save_at = img_dir + str(file_idx) + file_extension
				img_locations.append(save_at)
			file_idx += 1
			print(file_url)
			# excat code for download file to assigned location.
			urllib.request.urlretrieve(quote(file_url, safe=':/'), save_at)
		return (img_locations, pdf_locations)
