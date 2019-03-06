from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
import json
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Volcano400139@db/sub_pub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def event(topic, title, message):
    result = dict()
    result['topic'] = topic
    result['title'] = title
    result['message'] = message
    return result

def dbMessage(e,publisher):
    result = dict()
    result['publisher'] = publisher
    result['event'] = e
    # result['topic'] = e['topic']
    # result['message'] = e['message']
    # result['title'] = e['title']
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    result['time'] = date
    result['read'] = False
    return result


class sub(db.Model):
    __tablename__ = 'subscrible'
    id = db.Column(db.INTEGER,primary_key=True)
    user = db.Column(db.Text,unique = False)
    topic = db.Column(db.Text(length=(2**32)-1),unique = False)
    message = db.Column(db.Text(length=(2**32)-1),unique = False)

class pub(db.Model):
    __tablename__ = 'publish'
    id = db.Column(db.INTEGER,primary_key=True)
    user = db.Column(db.Text,unique = False)
    pub_list = db.Column(db.Text(length=(2**32)-1),unique = False)

def subscribe(username,topic):
    #check user
    check_user = sub.query.filter(sub.user == username).first()
    if(check_user == None):
        #add user to database
        topic_list = [topic]
        message_list = []
        info = sub(user = username, topic = json.dumps(topic_list), message = json.dumps(message_list))
        db.session.add(info)
        db.session.commit()
        return 1
    else:
        topic_list = json.loads(check_user.topic)
        if(topic in topic_list):
            return 0
        else:
            topic_list.append(topic)
            check_user.topic = json.dumps(topic_list)
            db.session.commit()
            return 1

def match(topic):
    user_list = sub.query.filter((sub.topic.contains('"' + topic + '"'))).all()
    return user_list


def notify(publisher,user_list,e):
    tip = []
    for person in user_list:
        name = person.user
        ins ='Succeed to send the message: ' + json.dumps(e) + ' to ' + name
        tip.append(ins)
        person = sub.query.filter(sub.user == name).first()
        message_list = json.loads(person.message)
        new_message = dbMessage(e,publisher)
        message_list.append(new_message)
        person.message = json.dumps(message_list)
        db.session.commit()
    return tip


def publish(publisher, e):
    user_list = match(e['topic'])
    person = pub.query.filter(pub.user == publisher).first()
    if(len(user_list) > 0):
        result = notify(publisher, user_list,e)
        user_name_list = [people.user for people in user_list]
        if (person == None):
            pub_list = []
            pub_content = dict()
            pub_content['Event'] = e
            pub_content['Subscribes'] = user_name_list
            pub_list.append(pub_content)
            publisher = pub(user = publisher, pub_list = json.dumps(pub_list))
            db.session.add(publisher)
            db.session.commit()
        else:
            pub_list = json.loads(person.pub_list)
            pub_content = dict()
            pub_content['Event'] = e
            pub_content['Subscribes'] = user_name_list
            pub_list.append(pub_content)
            person.pub_list = json.dumps(pub_list)
            db.session.commit()
        return result
    else:
        if (person == None):
            pub_list = []
            pub_content = dict()
            pub_content['Event'] = e
            pub_content['Subscribes'] = []
            pub_list.append(pub_content)
            publisher = pub(user = publisher, pub_list = json.dumps(pub_list))
            db.session.add(publisher)
            db.session.commit()
        else:
            pub_list = json.loads(person.pub_list)
            pub_content = dict()
            pub_content['Event'] = e
            pub_content['Subscribes'] = []
            pub_list.append(pub_content)
            person.pub_list = json.dumps(pub_list)
            db.session.commit()
        return ['Nobody subscribe ' + e['topic'] + ' .']

def readMessages(username):
    person = sub.query.filter(sub.user == username).first()
    message_list = json.loads(person.message)
    unread_messages = []
    all_messages = []
    for message in message_list:
        content = dict()
        content['publisher'] = message['publisher']
        content['event'] = message['event']
        content['time'] = message['time']
        if message['read'] == False:
            message['read'] = True
            unread_messages.append(content)
            all_messages.append(content)
        else:
            all_messages.append(content)
    person.message = json.dumps(message_list)
    db.session.commit()
    return unread_messages,all_messages

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/sub',methods = ['GET','POST'])
def sub_page():
    if request.method == "GET":
        return render_template('Sub1.html',method = 'GET')
    else:
        sub_user = request.form['sub_name']
        sub_topic = request.form['sub_topic']
        subscribe(sub_user,sub_topic)
        topic_list = json.loads(sub.query.filter(sub.user == sub_user).first().topic)
        topics_string = ''
        for topic in topic_list:
            topics_string += (topic+',')
        topics_string = topics_string[:-1]
        new_messages,all_messages = readMessages(sub_user)
        new_messages_string = ''
        all_messages_string = ''
        for a in new_messages:
            content = '%s: @%s %s\n' % (a['time'],a['publisher'],a['event'])
            new_messages_string += content
        for b in all_messages:
            content = '%s: @%s %s\n' % (b['time'],b['publisher'],b['event'])
            all_messages_string += content
        return render_template('Sub2.html',topics = topics_string, new_messages = new_messages_string,
                               all_messages = all_messages_string, method = 'POST')

@app.route('/pub',methods = ['GET','POST'])
def pub_page():
    if request.method == "GET":
        return render_template('Pub1.html',method = 'GET')
    else:
        publisher = request.form['user']
        topic = request.form['topic']
        title = request.form['title']
        message = request.form.get('message')
        e = event(topic,title,message)
        result = publish(publisher,e)
        send_log = ''
        for log in result:
            send_log += (log + '\n')

        return render_template('Pub2.html', send_logs = send_log, method = 'POST')


if __name__ == '__main__':
    db.create_all()
    app.run(debug = True,host='0.0.0.0')
