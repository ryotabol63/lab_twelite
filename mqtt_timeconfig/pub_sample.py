#!/usr/bin/env python
# coding: UTF-8

#################################################################
# Copyright (C) 2017 Mono Wireless Inc. All Rights Reserved.    #
# Released under MW-SLA-*J,*E (MONO WIRELESS SOFTWARE LICENSE   #
# AGREEMENT).                                                   #
#################################################################

# ライブラリのインポート
import sys
import csv
import os
import random
#import copy
#import threading
import serial
import paramiko
import time
import datetime
from optparse import *
#from queue import Queue

from time import sleep
import paho.mqtt.client as mqtt

# WONO WIRELESSのシリアル電文パーサなどのAPIのインポート
sys.path.append('./MNLib/')
from apppal import AppPAL

# ここより下はグローバル変数の宣言
# コマンドラインオプションで使用する変数
options = None
args = None

# 各種フラグ
bEnableLog = False
bEnableErrMsg = False

# プログラムバージョン
Ver = "1.1.0"

# mqtt 接続----------------------------------------------------------
sys.stderr.write("*** 開始 ***\n")
host = '192.168.11.4'
port = 1883
topic = 'TWELITE/'

client = mqtt.Client(protocol=mqtt.MQTTv311)

client.connect(host, port=port, keepalive=60)
client.loop_start()  #別スレッドでループ（keepalive）の実装




#CSVを開く

log_name = 'mqttpub' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') +'.csv'

print(log_name)

def writeX(note):
    with open(log_name,'a',encoding='shift_jis',newline='') as f:
        f.write(note + '\n')

if __name__ == '__main__':
    header = ','.join(['time','pubno'])
    writeX(header)



    for pubno in range(1000):
        try:
            pubno_4d = str(pubno).zfill(4)   #4桁に
            writeX(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + ',' + pubno_4d)
            send_data = pubno_4d + ',aaaaa' + 'aaaaaaaaaa' + 'aaaaaaaaaa' + 'aaaaaaaaaa' + 'aaaaaaaaaa'        #str50文字
            client.publish(topic, send_data)
        except KeyboardInterrupt:
            break
    
    client.loop_stop(force= False)
    client.disconnect()


    print("*** Exit App_PAL Viewer ***")
