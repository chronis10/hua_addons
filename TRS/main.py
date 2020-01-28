import logging
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import paho.mqtt.client as mqtt
import json
import random
incom = {"msg":""}
req_list = []
tele_api = ''
mqtt_auth = False
mqtt_username = ""
mqtt_password = ""
mqtt_server = "localhost"
mqtt_sub_topic = ""

class requests_obj():
    def __init__(self,userid,title,rec_id):
        self.userid = userid
        self.title = title
        self.response = -1
        self.status = "Waitting"
        self.time_start = time.time()
        self.user_informed = False
        self.rec_id = rec_id
        
    def time_dif(self):
        dif=time.time() - self.time_start
        if dif > 20:
            self.status = "Timeout"
            self.response = 0

    def status_item(self):
        print("{},{},{},{},{}".format(self.userid,self.title,self.response,self.status,self.rec_id))
    
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def update_rec(code,resp):
    global req_list
    for items in req_list:
        print(items.rec_id)
        print(code)
        if items.rec_id == code:
            items.response = resp
            if resp == 1:
                items.status = "Accepted"
            else:
                items.status = "Rejected"
                
                

def button(update, context):
    query = update.callback_query
    #print(update._id_attrs)
    code = query.data.split(',')[0].strip()
    resp = int(query.data.split(',')[1].strip())
    update_rec(code,resp)
    query.edit_message_text(text="Selected option: {}".format(query.data))

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    

def send_message(updater,userid,code,title):   
    
    keyboard = [[InlineKeyboardButton("Accept", callback_data=code+","+'1'),
                 InlineKeyboardButton("Reject", callback_data=code+","+'0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)    
    updater.bot.send_message(chat_id=userid, text=title,reply_markup=reply_markup)

def single_message(updater,userid,msg):
    updater.bot.send_message(chat_id=userid, text="Recomendation "+msg)
    
#MQTT
def on_message_msgs(mosq, obj, msg):
    global incom
    print(msg.payload.decode('utf-8'))
    incom = json.loads(msg.payload.decode('utf-8'))    
    print("MESSAGES: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_message(mosq, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def main():
    global incom,req_list,tele_api,mqtt_username,mqtt_auth,mqtt_password,mqtt_server,mqtt_sub_topic
    
    updater = Updater(tele_api, use_context=True)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    #updater.idle()
    mqttc = mqtt.Client()
    mqttc.message_callback_add(mqtt_sub_topic, on_message_msgs)    
    mqttc.on_message = on_message
    if mqtt_auth:
        mqttc.username_pw_set(mqtt_username, password=mqtt_password)
    mqttc.connect(mqtt_server, 1883, 60)
    mqttc.subscribe(mqtt_sub_topic, 0)
    mqttc.loop_start()
    print("Started")
    try:
        while True:
            print(incom["msg"])
            if incom["msg"] == "new":                
                print("Send Recomdetation")
                print(incom)
                code = str(random.randint(1000,9999))
                req_list.append(requests_obj(incom['userid'],incom['title'],code))
                send_message(updater,incom['userid'],code,incom['title'])
                incom = {"msg":""}
            for item in req_list:
                if not item.user_informed:
                    if item.status == "Waitting":                        
                        item.time_dif()
                    elif item.status == "Timeout":
                        single_message(updater,item.userid,"Timeout")
                        item.user_informed = True
                    elif item.status  == "Rejected":
                        single_message(updater,item.userid,"Rejected")
                        item.user_informed = True                        
                    elif item.status== "Accepted":
                        single_message(updater,item.userid,"Accepted")
                        item.user_informed = True                    
                item.status_item()    
            time.sleep(5)
    except KeyboardInterrupt:
        print("Exit")
    #except Exception as e:
    #    print(e)
    finally: 
        updater.stop()
        mqttc.loop_stop()

if __name__ == '__main__':
    with open('data/options.json') as config_file:
                data = json.load(config_file)
    tele_api = data['telegram_api']    
    mqtt_username = data['mqtt_username']    
    mqtt_password = data['mqtt_password']    
    mqtt_server = data['mqtt_server']    
    mqtt_sub_topic = data['mqtt_sub_topic']
    mqtt_auth = data['mqtt_auth']
    
    main()
