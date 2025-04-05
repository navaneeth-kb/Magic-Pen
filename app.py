from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Message
from datetime import datetime, timedelta
import uuid

import threading
import time


app = Flask(__name__)
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        content = request.form['message']
        token = uuid.uuid4().hex[:6]
        msg = Message(token=token, content=content)
        session = Session()
        session.add(msg)
        session.commit()
        return redirect(url_for('link_generated', token=token))
    return render_template('index.html')

@app.route('/link/<token>')
def link_generated(token):
    return render_template('link.html', link=request.host_url + 'view/' + token)

@app.route('/view/<token>')
def view_message(token):
    session = Session()
    msg = session.query(Message).filter_by(token=token).first()

    if not msg:
        return render_template('expired.html', reason="Message not found")

    if msg.is_viewed:
        if msg.viewed_at and datetime.utcnow() > msg.viewed_at + timedelta(minutes=5):
            return render_template('expired.html', reason="Message expired")
        return render_template('expired.html', reason="Message already viewed")

    msg.is_viewed = True
    msg.viewed_at = datetime.utcnow()
    session.commit()
    return render_template("view.html", message=msg.content, timeout=300)


if __name__ == '__main__':
    app.run(debug=True)

    # Background thread to delete expired messages
def cleanup_expired_messages():
    while True:
        now = datetime.utcnow()
        expired = session.query(Message).filter(
            Message.is_viewed == True,
            Message.viewed_at != None,
            Message.viewed_at + timedelta(minutes=5) < now
        ).all()
        for msg in expired:
            session.delete(msg)
        session.commit()
        time.sleep(60)  # check every minute

threading.Thread(target=cleanup_expired_messages, daemon=True).start()

