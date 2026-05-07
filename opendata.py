import json

with open("臺中市113年10月份十大高肇事路口.JSON", "r", encoding="utf-8") as file:
    jsondata = json.load(file)

for item in jsondata:
    print(item["路口名稱"], "原因:", item["主要肇因"])
    print()