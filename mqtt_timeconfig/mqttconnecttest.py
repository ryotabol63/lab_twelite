#!/usr/bin/env python
# coding: UTF-8

#MQTTによる時間取得プログラム
#enddevice側の実装

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


# mqtt 接続----------------------------------------------------------
sys.stderr.write("*** 開始 ***\n")
host = '127.0.0.1'                  #ブローカーのIP
port = 1883
pub_topic = 'timerequest/hoge/' 
#sub_topic = pub_topic
sub_topic = 'timereply/hoge/#'

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(client.topic)

def on_message_enddevice(client, userdata, message):
    nakami = message.payload
    message_json = nakami.decode('utf-8')                #受信データはバイト列なのでそれを文字列に変換する
    #print (message_json)
    #client.loop_stop()
    global test_message
    test_message = message_json
    #client.loop_stop()                                   #今回は1回受信すればいいので受信したら閉じる
    print('受信')
    #print (type(message_json))


def publishrequest(client_pub):
    time.sleep(0.2)
    client_pub.publish(pub_topic, 'testmessage')



client_pub = mqtt.Client(protocol=mqtt.MQTTv311)

client_pub.connect(host, port=port, keepalive=60)
#client_pub.loop_start()  #publish側のclientの開始（keepalive）
#client_sub = mqtt.Client(protocol=mqtt.MQTTv311)

#sleeptime = 11.0
#attemptno = 1
'''
while test_message == 'hoge':
    time.sleep(1.0)
    if attemptno > 9:
        sys.stderr.write('failed')
        sys.exit(1)
    print('attempt {}'.format(attemptno))
    attemptno += 1
    test_message = 'hoge'
    client_sub = mqtt.Client(protocol=mqtt.MQTTv311)
    client_sub.topic = sub_topic         #on_connectでsubscribeする
    client_sub.on_connect = on_connect
    client_sub.on_message = on_message_enddevice
    client_sub.connect(host, port=port, keepalive=60)
    # ループ
    print('test1')
    client_sub.loop_start()
    time.sleep(0.2)
    print('test2')
    publishrequest(client_pub)
    time.sleep(1.5)    #受信にかかる時間は2秒まで許容
    client_sub.loop_stop()


time.sleep(0.2)
#time.sleep(0.2)
'''
print(test_message)

while True:
    client_pub.subscribe('hoge')
    time.sleep(2.0)
    client_pub.unsubscribe('hoge')
    print('hoge')