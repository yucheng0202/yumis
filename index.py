import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template,request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)


app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入徐宇呈的網站20260409</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href=/welcome?u=宇呈&d=靜宜資管&c=資訊管理導論>Get傳值</a><hr>"
    link += "<a href=/account>POST傳值</a><hr>"
    link += "<a href=/math>次方根號</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/read2>讀取Firestore資料(根據姓名關鍵字：楊)</a><hr>"
    link += "<a href=/spider1>爬取子青老師本學期課程</a><hr>"
    link += "<a href=/movie1>即將上映電影</a><hr>"
    return link


@app.route("/movie1")
def movie1():
    q = request.args.get("q", "")
    Result = ""

    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"

    sp = BeautifulSoup(Data.text, "html.parser")
    results = sp.select(".filmListAllX li")

    for item in results:
        title = item.find("img").get("alt")
        if q in title:
            introduce = "http://www.atmovies.com.tw" + item.find("a").get("href")
            post = "http://www.atmovies.com.tw" + item.find("img").get("src")

            Result += "<a href='" + introduce + "'>" + title + "</a><br>"
            Result += "<img src='" + post + "'><br><br>"

    if Result == "":
        Result = "查無結果"

    return render_template("hello2.html", result=Result)

@app.route("/spider1")
def spider1():
    Result = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url, verify=False)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")

    for i in result:
        Result += i.text +  i.get("href") + "<br>"
    return Result

@app.route("/")
def home():
    return render_template("hello.html", result="")

@app.route("/read2")
def read2():
    keyword = request.args.get("keyword")

    if keyword is None or keyword.strip() == "":
        return render_template("hello.html", result="請輸入老師姓名關鍵字")

    db = firestore.client()
    collection_ref = db.collection("靜宜資管2026B")
    docs = collection_ref.get()

    result = ""

    for doc in docs:
        teacher = doc.to_dict()
        print("teacher =", teacher)

        if "name" in teacher and "lab" in teacher:
            if keyword in str(teacher["name"]):
                result += f"{teacher['name']} 老師的研究室在 {teacher['lab']}<br>"

    if result == "":
        result = f"查無資料，關鍵字是：{keyword}"

    result = f"查詢結果（關鍵字：{keyword}）：<br><br>" + result

    return render_template("hello.html", result=result)


@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管2026B")    
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()
    for doc in docs:
        Result += str(doc.to_dict()) + "<br>"    
    return Result


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html",datetime = str(now))

@app.route("/me")
def me():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name= user, dep=d, course=c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    result = None
    if request.method == "POST":
        x = int(request.form["x"])
        y = int(request.form["y"])
        opt = request.form["opt"]

        if opt == "a":
            result = x ** y
        elif opt == "b":
            if y == 0:
                result = "不能開0次方根"
            else:
                result = x ** (1/y)

    return render_template("math.html", result=result)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
