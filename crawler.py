from function.downloadHTML import downloadHTML
from function.downloadFILE import downloadFILE
from function.extractMap import extractMap
from function.getLatest import getLatest
from config import access_key, secret_access_key
from function.reachDB import getDBConnect
# Test Case:
# 77443 第一個開始提供英文資訊的報告
# 77445 從這版開始,改了軍機架次的呈現方式
# 77448
# 77614
#for pid in range(77523, 77915):
#	print(pid , "result code: ", downloadHTML(pid))

print(77599, "result code: ", downloadHTML(77599))

#locations = downloadFILE(77871)
#print(locations)
#print(extractMap(77871, locations[1]))
#print(getLatest())
