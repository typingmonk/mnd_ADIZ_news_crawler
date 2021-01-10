from function.downloadHTML import requestPage 

# Test Case:
# 71207 (無文章、被轉址回首頁)
# 77871（有文章、是軍機繞台的消息）
# 71221（有文章、是無關軍機繞台的消息）
print(requestPage(71207))
print(requestPage(77871))
print(requestPage(71221))
