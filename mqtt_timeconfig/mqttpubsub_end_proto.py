#!/usr/bin/env python
# coding: UTF-8

#MQTTによる時間取得プログラム
#enddevice側の実装

import sys
import os
import datetime
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
time_offset = 0
reply_topic = 'initial'


# mqtt 接続----------------------------------------------------------
sys.stderr.write("*** 開始 ***\n")
host = '127.0.0.1'                  #ブローカーのIP
port = 1883
pub_topic_base = 'timerequest/hoge/' 
#sub_topic = pub_topic
sub_topic = 'timereply/hoge/#'

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(client.topic)

def on_message_enddevice(client, userdata, message):
    reply_topic = message.topic
    replyno = reply_topic.split('/')[-2]
    print(replyno)
    if int(replyno) == attemptno:
        message_body = message.payload
        message_decode = message_body.decode('utf-8')                #受信データはバイト列なのでそれを文字列に変換する
        #print (message_json)
        #client.loop_stop()
        global time_offset
        time_by_host = datetime.datetime.fromisoformat(message_decode)
        rec_time = datetime.datetime.now()
        time_offset = time_by_host - rec_time
        #print(time_offset)
        print(rec_time.isoformat())
        #client.loop_stop()                                   #今回は1回受信すればいいので受信したら閉じる
        print('正常受信')
        #print (type(message_json))
    else:
        print('遅れ受信')


def publishrequest(client_pub, attemptno):
    pub_topic = pub_topic_base + str(attemptno) + '/'
    client_pub.publish(pub_topic, 'testmessage')



client_pub = mqtt.Client(protocol=mqtt.MQTTv311)

client_pub.connect(host, port=port, keepalive=60)
client_pub.loop_start()  #publish側のclientの開始（keepalive）
client_sub = mqtt.Client(protocol=mqtt.MQTTv311)

sleeptime = 11.0
attemptno = 1
client_sub = mqtt.Client(protocol=mqtt.MQTTv311)
client_sub.topic = sub_topic         #on_connectでsubscribeする
client_sub.on_connect = on_connect
client_sub.on_message = on_message_enddevice
client_sub.connect(host, port=port, keepalive=60)
print('test1')
client_sub.loop_start()

while time_offset == 0:
    if attemptno > 9:
        sys.stderr.write('failed')
        sys.exit(1)
    print('attempt {}'.format(attemptno))
    client_sub = mqtt.Client(protocol=mqtt.MQTTv311)
    client_sub.topic = sub_topic         #on_connectでsubscribeする
    client_sub.on_connect = on_connect
    client_sub.on_message = on_message_enddevice
    client_sub.connect(host, port=port, keepalive=60)
    req_time = datetime.datetime.now()
    print(req_time.isoformat())
    publishrequest(client_pub, attemptno)
    time.sleep(1.0)    #受信にかかる時間は1秒まで許容
    attemptno += 1


time.sleep(0.2)
#time.sleep(0.2)
print(time_offset)
