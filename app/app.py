#!/usr/bin/env python3

from flask import Flask
import psycopg2
import smtplib
import ssl
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
try:
    conn = psycopg2.connect("host={} dbname={} password={} user={}".format(os.getenv(
        "POSTGRES_URL", "localhost"), os.getenv("POSTGRES_DB"), os.getenv("POSTGRES_PWD"), os.getenv("POSTGRES_USER")))
except psycopg2.Error as err:
    print("[-] Error psql: {}".format(err.pgerror))
    quit(1)
conn.autocommit = True
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS site(url CHAR(200) NOT NULL, category CHAR(200) NOT NULL, id SERIAL PRIMARY KEY NOT NULL)")


@app.route('/')
def hello():
    return "Hello, this is not a website"


@app.route('/<url>')
def xana(url):
    postgreSQL_select_Query = "SELECT category, url FROM site WHERE url = %s"
    cur.execute(postgreSQL_select_Query, (url,))
    result = cur.fetchall()
    if result:
        return result[0]
    return "Error 400 bad URL"


@app.route('/find/<category>')
def sendCategory(category):
    x = 1
    site = ""
    max_count = 0
    if (check_in_list(category)):
        postgreSQL_select_Count = "SELECT COUNT(category) FROM site WHERE category = %s"
        cur.execute(postgreSQL_select_Count, (category,))
        max_count = cur.fetchall()
        max_count = int(max_count[0][0])
        postgreSQL_select_Query = "SELECT url, category FROM site WHERE category = %s"
        cur.execute(postgreSQL_select_Query, (category,))
        result = cur.fetchall()
        site = result[0][0]
        while x <= max_count - 1:
            site = site + ", " + result[x][0]
            x = x + 1
        return site
    else:
        return "Error 400 category not found"


@app.route("/<url>/<category>")
def reportError(url, category):
    if check_in_list(category):
        smtp_address = "{}".format(os.getenv("STMP_ADDRESS"))
        smtp_port = 465

        email_address = "{}".format(os.getenv("EMAIL_ADDRESS"))
        email_password = "{}".format(os.getenv("EMAIL_PASSWORD"))

        email_receiver = "{}".format(os.getenv("EMAIL_RECEIVER"))

        message = MIMEMultipart("alternative")
        message["Subject"] = "[Xana] Category change"
        message["From"] = "{}".format(os.getenv("EMAIL_ADDRESS"))
        message["To"] = "{}".format(os.getenv("EMAIL_RECEIVER"))

        text = '''
            Bonjour,

            Un nouveau utilisateur a proposé une modification/nouvelle catégorie pour le site:
            {} : {}
            Vous pouvez l'ajouter à la base de données de xana.

            Bonne journée à vous,
            la joyeuse équipe de ViVi
        '''.format(url, category)

        texte_mine = MIMEText(text, 'plain')

        message.attach(texte_mine)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, email_receiver, message.as_string())
        notify_discord(url, category)
        return url
    else:
        return "Error 400 category"


def check_in_list(category):
    sites = [
        "search engine",
        "entertainment",
        "mail manager",
        "merchandising",
        "social network",
        "information",
        "working tool",
        "bank / payment method",
        "pornography",
        "online storage",
        "education",
        "government / public service",
        "religion",
        "health"
    ]
    x = 0
    while x <= 13:
        if (sites[x] == category):
            print(sites[x] + category)
            return True
        x = x + 1
    return False


def notify_discord(url, category):
    requests.post(os.getenv("HOOK_URL"), {
        "content": "Only react with ✅ or ❌",
        "embeds": [{
            "title": "Categorization Request",
            "description": "Someone submitted a request",
            "image": {
                "url": "https://favicon.splitbee.io/?url={}".format(url)
            },
            "fields": [{
                "name": "Url",
                "value": url
            }, {
                "name": "Category",
                "value": category
            }],
            "footer": {
                "text": "Made in ViVi"
            }
        }]
    })


if __name__ == '__main__':
    app.run()
