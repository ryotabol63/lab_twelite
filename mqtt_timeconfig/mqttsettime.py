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


def mqttsettime(host, topic):

    #関数内変数（意味合い的にglobalに近い）
    time_offset = 0
    sys.stderr.write("*** Request time from  {}***\n".format(host))

    # mqtt 接続----------------------------------------------------------
    
    host = host                  #ブローカーのIP
    port = 1883
    pub_topic_base = 'timerequest/' + topic 
    #sub_topic = pub_topic
    sub_topic = 'timereply/' + topic + '#'

    def on_connect(client, userdata, flags, respons_code):
        print('status {0}'.format(respons_code))
        client.subscribe(client.topic)

    def on_message_enddevice(client, userdata, message):
        #メッセージを受信したときに正しいtopic(最新の番号)になっているかチェックする
        reply_topic = message.topic
        replyno = reply_topic.split('/')[-2]
        print(replyno)
        if int(replyno) == attemptno:
            message_body = message.payload
            message_decode = message_body.decode('utf-8')                #受信データはバイト列なのでそれを文字列に変換する
            #print (message_json)
            #client.loop_stop()
            nonlocal time_offset      #一つ外の文字を参照したい場合
            time_by_host = datetime.datetime.fromisoformat(message_decode)
            rec_time = datetime.datetime.now()
            time_offset = time_by_host - rec_time
            #print(time_offset)
            print('正常受信')
            print(rec_time.isoformat())
            #client.loop_stop()                                   #今回は1回受信すればいいので受信したら閉じる
            #print (type(message_json))
        else:
            print('遅れ受信')


    def publishrequest(client, attemptno):
        pub_topic = pub_topic_base + str(attemptno) + '/'
        client.publish(pub_topic, 'testmessage')


    #sleeptime = 11.0
    
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.topic = sub_topic         #on_connectでsubscribeする
    client.on_connect = on_connect
    client.on_message = on_message_enddevice
    client.connect(host, port=port, keepalive=60)
    print('test1')
    client.loop_start()

    attemptno = 1
    while time_offset == 0:
        if attemptno > 9:        #10回までチェック
            sys.stderr.write('failed')
            sys.exit(1)
        print('attempt {}'.format(attemptno))
        
        req_time = datetime.datetime.now()
        print(req_time.isoformat())
        publishrequest(client, attemptno)
        time.sleep(1.0)    #受信にかかる時間は1秒まで許容
        attemptno += 1


    time.sleep(0.2)
    #time.sleep(0.2)
    print(time_offset)
    return(time_offset)


if __name__ == '__main__':
    mqttsettime('127.0.0.1', 'hoge/')