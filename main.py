from workers import Response
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

# --------------------
# 🔧 Gmailアカウント情報
# --------------------
gmail_user = 'danbouru0607@gmail.com'  # ← あなたのGmail
app_password = 'biej bgvq hrvs wrmh'  # ← アプリパスワード（16桁）

# --------------------
# 🌐 スクレイピング処理（重複を排除）
# --------------------
url = 'https://sunabaco.com/event'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

event_text = ""
event_links = soup.select('.eventWrap a')  # すべてのイベント<a>を取得

seen = set()  # ← 重複防止のためのセット

event_number = 1
for a_tag in event_links:
    title_tag = a_tag.select_one('h4.eventCard__name')
    date_tag = a_tag.select_one('span.eventCard__date')
    link = a_tag['href']

    if title_tag and date_tag:
        title = title_tag.get_text(strip=True)
        date = date_tag.get_text(strip=True)

        # 🔁 重複チェック：タイトル＋リンクのセットで確認
        identifier = (title, link)
        if identifier in seen:
            continue  # → すでに取得済みなのでスキップ
        seen.add(identifier)

        event_text += f"\n【イベント{event_number}】\n"
        event_text += f"タイトル: {title}\n"
        event_text += f"{date}\n"
        event_text += f"リンク: {link}\n"
        event_number += 1

if not event_text:
    event_text = "現在、イベント情報は見つかりませんでした。"

# --------------------
# 📧 メールの準備と送信
# --------------------
to = gmail_user
subject = 'SUNABACOイベント情報のお知らせ'
body = f"""こんにちは！

SUNABACOのイベントページから最新のイベント情報を取得しました📅

{event_text}

自動送信メールより
"""

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = gmail_user
msg['To'] = to

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_user, app_password)
        server.send_message(msg)
        print('メール送信成功！')
except Exception as e:
    print('エラー:', e)
