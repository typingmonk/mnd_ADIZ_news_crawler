from pathlib import Path
import urllib.request as request
import bs4 as bs

# return value:
# 0 : 該網址被轉址、或是404
# 1 : 是貼文、而且是跟軍機繞台有關的貼文
# 2 : 是貼文但跟軍機繞台無關
def requestPage(pid):
	html_page = request.urlopen("https://www.mnd.gov.tw/Publish.aspx?p=" + str(pid)).read()
	soup = bs.BeautifulSoup(html_page, "html.parser")
	#確認是一則貼文，其餘可能是被轉址或錯誤頁面。
	if "thisPages" in str(soup):
		return getHTML(soup,pid)
	else:
		return 0

# reutrn value:
# 1 : 是貼文、而且是跟軍機繞台有關的貼文
# 2 : 是貼文但跟軍機繞台無關
def getHTML(soup,pid):
	current_path = Path(__file__).parent.absolute()
	save_location = str(current_path.parent) + "/html/" + str(pid) + ".html"
	thisPages = soup.find_all("div", class_="thisPages")
	thisPages_str = str(thisPages[0])
	with open(save_location, 'w') as file:
		file.write(thisPages_str)

	if "軍機" in thisPages_str:
		return 1
	else:
		return 2
