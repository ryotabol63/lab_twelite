#!/usr/bin/env python
# coding: UTF-8

#MQTTによる時間取得プログラム
#host側の実装

import sys
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import paho.mqtt.client as mqtt

# ここより下はグローバル変数の宣言
# コマンドラインオプションで使用する変数
options = None
args = None

# 各種フラグ
bEnableLog = False
bEnableErrMsg = False

#グローバル変数
test_message = 'hoge'
test_num = 0


# mqtt 接続----------------------------------------------------------
sys.stderr.write("*** 開始 ***\n")
host = '127.0.0.1'                  #ブローカーのIP
port = 1883 
sub_topic = 'timerequest/#'
#pubtopicは動的に決定

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(client.topic)

def on_message_host(client, userdata, message):
    global test_num
    if test_num == 0:
        time.sleep(4.0)
        test_num += 1
    request_topic = message.topic
    slash = request_topic.find('/')
    request_id = request_topic[(slash + 1):]
    pub_topic = 'timereply/' + request_id
    nakami = message.payload
    message_json = nakami.decode('utf-8')                #受信データはバイト列なのでそれを文字列に変換する
    print (message_json)
    print('受信')
    client.publish(pub_topic, 'reply')
    print('送信')
    #print (type(message_json))





client = mqtt.Client(protocol=mqtt.MQTTv311)

client.topic = sub_topic
client.on_connect = on_connect
client.on_message = on_message_host
client.connect(host, port=port, keepalive=60)
# ループ
print('test1')

client.loop_forever()




