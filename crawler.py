from function.downloadHTML import downloadHTML
from function.downloadPDF  import downloadPDF
from function.extractFlightRecords import save_TB_flight_records
from function.getLatest import getLatest
#from function.downloadFILE import downloadFILE
#from function.extractMap import extractMap

target_id, latest_DB_date, latest_date = getLatest()
while latest_DB_date < latest_date:
	target_id += 1
	result = downloadHTML(target_id)
	if result is not None:
		latest_DB_date = result
		save_TB_flight_records(target_id)
		downloadPDF(target_id)
		print(target_id, latest_DB_date)
	else:
		print(target_id, None)
print("Done.")
