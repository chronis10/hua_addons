import logging
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import paho.mqtt.client as mqtt
import json
import random
import mysql.connector
import datetime

#REQUEST CLASS
class requests_obj():
    def __init__(self,userid,title,rec_id,timeout):
        self.userid = userid
        self.title = title
        self.response = -1
        self.status = "Waitting"
        self.time_start = datetime.datetime.now()
        self.user_informed = False
        self.rec_id = rec_id
        self.time_finished = None
        self.entity = "Dummy"
        self.timeout = timeout

    def time_dif(self):
        dif=abs(datetime.datetime.now() - self.time_start).seconds
        if dif > self.timeout:
            self.status = "Timeout"
            self.response = 0

    def status_item(self):
        print("{},{},{},{},{}".format(self.userid,self.title,self.response,self.status,self.rec_id))

#TELEGRAM
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def update_rec(code,resp):
    global req_list
    for items in req_list:
        if items.rec_id == code:
            items.response = resp
            if resp == 1:
                items.status = "Accepted"
            else:
                items.status = "Rejected"


def button(update, context):
    query = update.callback_query
    code = query.data.split(',')[0].strip()
    resp = int(query.data.split(',')[1].strip())
    update_rec(code,resp)
    if resp == 1:
        answer = "Accepted"
    else:
        answer = "Rejected"
    query.edit_message_text(text="Recommendation {}".format(answer))

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(updater,userid,code,title):
    keyboard = [[InlineKeyboardButton("Accept", callback_data=code+","+'1'),
                 InlineKeyboardButton("Reject", callback_data=code+","+'0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    updater.bot.send_message(chat_id=userid, text=title,reply_markup=reply_markup)

def single_message(updater,userid,msg):
    updater.bot.send_message(chat_id=userid, text="Recommendation "+msg)

#MQTT
def on_message_msgs(mosq, obj, msg):
    global incom
    incom = json.loads(msg.payload.decode('utf-8'))
    print("MESSAGES: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_message(mosq, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


#BUFFER LIST CLEANER
def clean_buffer():
    global req_list
    cleaner = True
    for items in req_list:
        if items.user_informed == True:
            req_list.remove(items)

#MYSQL
def store_mysql():
    global req_list,data
    new_data = False
    try:

        for items in req_list:
            if items.user_informed:
                if not new_data:
                    mydb = mysql.connector.connect(
                      host= data['db_ip'],
					  port=data['db_port'],
                      user= data['db_username'],
                      passwd= data['db_password'],
                      database= data['db_name'])
                    mycursor = mydb.cursor()
                mycursor.execute(("INSERT INTO {}.{} (user_id, notify_time, response_time,"
                 "question, response, response_log, entity) VALUES ('{}','{}',"
                 "'{}','{}','{}','{}','{}');").format(data['db_name'],
                                     data['db_table'],
                                     items.userid,
                                     items.time_start,
                                     items.time_finished,
                                     items.title,
                                     items.response,
                                     items.status,
                                     items.entity))
                req_list.remove(items)
                new_data = True
        if new_data:
            mydb.commit()
            mydb.close()
            print("Database updated")
    except Exception as e:
        print("Database update failed")
        print(e)



def main():
    global incom,req_list,data
    updater = Updater(data['telegram_api'], use_context=True)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    mqttc = mqtt.Client()
    mqttc.message_callback_add(data['mqtt_sub_topic'], on_message_msgs)
    mqttc.on_message = on_message
    if data['mqtt_auth']:
        mqttc.username_pw_set(data['mqtt_username'], password=data['mqtt_password'])
    mqttc.connect(data['mqtt_server'], 1883, 60)
    mqttc.subscribe(data['mqtt_sub_topic'], 0)
    mqttc.loop_start()
    print("Started")
    try:
        while True:
            if incom["msg"] == "new":
                print("Send Recomdetation")
                code = str(random.randint(1000,9999))
                req_list.append(requests_obj(incom['userid'],incom['title'],code,data['timeout']))
                send_message(updater,incom['userid'],code,incom['title'])
                incom = {"msg":""}
            for item in req_list:
                if not item.user_informed:
                    if item.status == "Waitting":
                        item.time_dif()
                    elif item.status == "Timeout":
                        single_message(updater,item.userid,"Timeout")
                        item.time_finished = datetime.datetime.now()
                        item.user_informed = True
                    elif item.status  == "Rejected":
                        item.time_finished = datetime.datetime.now()
                        item.user_informed = True
                    elif item.status== "Accepted":
                        item.time_finished = datetime.datetime.now()
                        item.user_informed = True
                item.status_item()
                if data['store_on_db']:
                    store_mysql()
                else:
                    clean_buffer()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Exit")
    #except Exception as e:
    #    print(e)
    finally:
        updater.stop()
        mqttc.loop_stop()

if __name__ == '__main__':
    incom = {"msg":""}
    req_list = []
    with open('data/options.json') as config_file:
                data = json.load(config_file)
    main()
