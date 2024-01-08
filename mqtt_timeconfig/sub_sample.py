# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
#import influxdb
import datetime
import random
import json
import csv

#import partcsv

#for MQTT broker
MQTT_HOST = '127.0.0.1'
MQTT_PORT = 1883
KEEP_ALIVE = 60
TOPIC = 'TWELITE/#'

#for InfluxDB
#DB_HOST = '127.0.0.1'
#DB_PORT = 8086
#DB_NAME = 'influx_iot01'
#DB_MEASUREMENT = 'table1'

#db = influxdb.InfluxDBClient(
    #host='localhost',
    #port=8086,
    #database='influx_iot01'
#)

"""
接続を試みたときに実行
def on_connect(client, userdata, flags, respons_code):

* client
Clientクラスのインスタンス

* userdata
任意のタイプのデータで新たなClientクラスののインスタンスを作成するときに>設定することができる

* flags
応答フラグが含まれる辞書
クリーンセッションを0に設定しているユーザに有効。
セッションがまだ存在しているかどうかを判定する。
クリーンセッションが0のときは以前に接続したユーザに再接続する。

0 : セッションが存在していない
1 : セッションが存在している

* respons_code
レスポンスコードは接続が成功しているかどうかを示す。
0: 接続成功
1: 接続失敗 - incorrect protocol version
2: 接続失敗 - invalid client identifier
3: 接続失敗 - server unavailable
4: 接続失敗 - bad username or password
5: 接続失敗 - not authorised
"""

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(client.topic)

"""
def on_message(client, userdata, message):
topicを受信したときに実行する
"""
def on_message(client, userdata, message):
    #時間計測
    time_start = datetime.datetime.now()
    print(time_start.strftime('%Y/%m/%d %H:%M:%S.%f'))
    nakami = message.payload
    print(nakami)
    #message_json = message.payload
    #message_json = nakami.decode('utf-8')                #受信データはバイト列なのでそれを文字列に変換する
    #print(message_json)
    #print (type(message_json))
    time_mid = datetime.datetime.now()
    print(time_mid.strftime('%Y/%m/%d %H:%M:%S.%f'))

    with open(mqttlog_name, 'a', encoding='shift-jis',newline='') as f:
        
        current_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
        f.write('\n' + current_time + ',')
    time_3 = time_mid = datetime.datetime.now()
    print(time_3.strftime('%Y/%m/%d %H:%M:%S.%f'))

    with open(mqttlog_name, 'ab') as f:
        f.write(nakami)

    #終わり時間
    time_finish = datetime.datetime.now()
    print(time_finish.strftime('%Y/%m/%d %H:%M:%S.%f'))
    print(time_finish - time_start)
    #すでにコンマ区切りされたデータなので単にwriteするだけ+改行
    #message_dict=json.loads(message_json)
    #print(message_dict)
    #write_to_influxdb(message_dict)


if __name__ == '__main__':
    mqttlog_name = 'mqtt_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'

    with open(mqttlog_name, 'a', encoding='shift-jis',newline='') as f:
        header =','.join(['time', 'data'])
        f.write(header)                        #すでにコンマ区切りされたデータなので単にwriteするだけ+改行

    while 1:
        try:

            client = mqtt.Client(protocol=mqtt.MQTTv311)
            client.topic = TOPIC# + '/' + tagname

            client.on_connect = on_connect
            client.on_message = on_message

            client.connect(MQTT_HOST, port=MQTT_PORT, keepalive=KEEP_ALIVE)

            # ループ
            client.loop_forever()       
        except KeyboardInterrupt:
            print('end')
            break           

print("終了処理中です。")
