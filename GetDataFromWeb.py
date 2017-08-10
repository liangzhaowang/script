import urllib2
import urllib
import cookielib
import json

loginurl = "https://gta.intel.com/auth/login"
url = "https://gta.intel.com/api/tp/v1/grid/TP-3719?requestId=2bace62f-0c1b-4b01-b1a4-e924607fd98e&offset=400&limit=200&compression_level=L3&timestamp=2017-03-22T02%3A25%3A52.643344Z"
# url = "https://gta.intel.com/#/testplanning/plan/TP-3719"
data={"username":"wangninx","password":"password_2"}
headers ={"User-agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1"}
post_data=urllib.urlencode(data)
cj=cookielib.CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
req=urllib2.Request(loginurl,post_data,headers)
result = opener.open(req)
result = opener.open(url)
obj = json.loads(result.read())
result = []
for row in obj["data"]:
    row_tmp = [row["testItem"]["itemId"], row["testItem"]["name"], row["path"][0] + ">" + row["path"][0], row["testPlan"]["name"], row["testItem"]["plugin"], row["testItem"]["arguments"], row["testItem"]["namespace"], row["effectiveAttributes"][0]["val"]]
    for ps in row["effectiveConfiguration"]["parameters"]:
        row_tmp.append(ps["val"])
    result.append(tuple(row_tmp))
print result