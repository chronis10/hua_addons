import json
import mysql.connector
from requests import post,get
from datetime import datetime,timedelta
import time

def get_hassio_data(data,entity_id,query_day):
    changes = []
    headers = {
    "Authorization": "Bearer " + data["hassio_api"],
    "content-type": "application/json",
    }
    url = "{}/api/history/period/{}T00:00:00+00:00?filter_entity_id={}".format(data["hassio_ip"],query_day,entity_id)
    r = get(url = url, headers=headers)
    if len(r.json()) > 0:
        for item in r.json()[0]:
            if item['state'] != 'unavailable':
                datetimeObj = datetime.strptime(item['last_changed'].split('+')[0].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                changes.append({'entity_id':item['entity_id'],'last_changed':datetimeObj,'state':item['state']})
                # print(item['entity_id'])
                # print(item['last_changed'])
                # print(item['state'])
        return changes
    else:
        return None

def get_hassio_around(data,entity_id,query_day):
    start_period = query_day + timedelta(seconds=data["time_delta"])
    #- delta time
    #end_period = query_day - timedelta(seconds=time_delta)
    s_period = start_period.strftime('%Y-%m-%dT%H:%M:%S')
    e_period = query_day.strftime("%Y-%m-%dT%H#%M#%S")
    e_period= e_period.replace('#','%3A')

    changes = []
    headers = {
    "Authorization": "Bearer " + data["hassio_api"],
    "content-type": "application/json",
    }
    url = ("{}/api/history/period/{}+00:00?"
    "end_time={}%2B00%3A00"
    "&filter_entity_id={}").format(data["hassio_ip"],s_period,e_period,entity_id)
    r = get(url = url, headers=headers)
    if len(r.json())>0:
        for item in r.json()[0]:
            if item['state'] != 'unavailable':
                datetimeObj = datetime.strptime(item['last_changed'].split('+')[0].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                changes.append({'entity_id':item['entity_id'],'last_changed':datetimeObj,'state':item['state']})
        return changes
    else:
        return None

def make_average(value_list):
    sum = 0
    print(value_list)
    if 'weather' in value_list[0]['entity_id'] or 'sun' in value_list[0]['entity_id']:
        return value_list[0]['state']
    else:
        for i,it in enumerate(value_list):
            
            if it['state'] == 'on':
                sum += 1
            elif it['state'] == 'off':
                pass
            else:
                sum += float(it['state'])
        value = sum/(i+1)
        return value


def get_entities(data):
    mydb = mysql.connector.connect(
        host= data['db_ip'],
		port=data['db_port'],
        user= data['db_username'],
        passwd= data['db_password'],
        database= data['db_name'])

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM {}".format(data['db_entities']))
    entities_list = mycursor.fetchall()
    print(len(entities_list))
    mydb.close()
    return entities_list

def store_to_db(data,data_list):
    mydb = mysql.connector.connect(
        host= data['db_ip'],
		port=data['db_port'],
        user= data['db_username'],
        passwd= data['db_password'],
        database= data['db_name'])

    mycursor = mydb.cursor()
    for dt in data_list:
        mycursor.execute("INSERT INTO {} ( `entity_id`,`time_changed`, `state`, `context`) VALUES ('{}', '{}', '{}', '{}');".format(data['db_recorder'],dt[0]['entity_id'],dt[0]['last_changed'],dt[0]['state'],json.dumps(dt[1])))

    mydb.commit()
    mydb.close()


def main(data,query_day):
    for_export=[]
    entities_list = get_entities(data)
    for entity in entities_list:
        print(entity[1])
        changes = get_hassio_data(data,entity[1],query_day)
        if changes is not None:
            for items in changes:
                temp_main = []
                temp_main.append(items)
                temp_sub = []
                for et in json.loads(entity[2]):
                    re = get_hassio_around(data,et['entity_id'],items['last_changed'])
                    temp_sub.append({'entity_id':et['entity_id'],'state':make_average(re)})
                temp_main.append(temp_sub)
                for_export.append(temp_main)
    print(for_export[0])
    store_to_db(data,for_export)


    # changes = get_hassio_data(data,'switch.water_heater','2020-02-03')
    # for items in changes:
    #     print(items)
    #     re = get_hassio_around(data,'switch.office_light',items['last_changed'],900)
    #     print(make_average(re))



if __name__ == '__main__':
    with open('data/options.json') as config_file:
        data = json.load(config_file)

    if data['debug'] == True:
        print('Debug mode')
        print(datetime.today().strftime('%Y-%m-%d'))
        main(data,datetime.today().strftime('%Y-%m-%d'))
    else:
        x=datetime.today() - timedelta(days=1)
        while True:
            if (datetime.today() - x ).days > 0:
                print('Scan {}'.format(datetime.today()))
                main(data,x.strftime('%Y-%m-%d'))
                x=datetime.today()
            print('Sleep {}'.format(datetime.today()))
            time.sleep(86400)
