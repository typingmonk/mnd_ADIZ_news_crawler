from pathlib import Path
from pdf2image import convert_from_path

current_path = Path(__file__).parent.absolute()
root_path = str(current_path.parent)
img_dir = root_path + "/img/"
pdf_dir = root_path + "/pdf/"

def extractMap(pid, pdf_locations):
	map_locations = list()
	for i, pdf_path in enumerate(pdf_locations):
		page = convert_from_path(pdf_path, dpi=200, first_page=2, last_page=2)[0]
		map_locations.append(img_dir + str(pid) + "_" + str(i) + "_map.jpg")
		page.save(img_dir + str(pid) + "_" + str(i) + "_map.jpg", "JPEG")
	return map_locations
