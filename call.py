from function.downloadHTML import requestPage 
from function.downloadFILE import downloadFILE
from function.extractMap import extractMap
from config import access_key, secret_access_key

# Test Case:
# 71207 (無文章、被轉址回首頁)
# 77871（有文章、是軍機繞台的消息）
# 71221（有文章、是無關軍機繞台的消息）
#print(requestPage(77871))
#locations = downloadFILE(77871)
#print(locations)
#print(extractMap(77871, locations[1]))
