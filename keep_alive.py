import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running on Render!"

def run():
    # هنا السطر السحري: سيقرأ البورت من Render تلقائياً، وإلا سيضع 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
