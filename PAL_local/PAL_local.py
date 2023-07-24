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
#import os
#import copy
#import threading
#import time
import datetime
from optparse import *
import random
#from queue import Queue

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

#CSVを開く

shortlog_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')) + '(' + str(random.randint(100, 999)) + ').csv'
#ゆくゆくサーバーに送信することを想定して、乱数をつけて重複を避ける

print(shortlog_name)

#データを取得するメイン部分。newline=''は改行をなくすためのオプション
with open(shortlog_name,'w',encoding='shift_jis',newline='') as f:

	header =['時間', '論理ID', 'タグID', '中継器ID', '送信番号', '電波強度', '電源電圧']

	csvout=csv.writer(f)

	csvout.writerow(header)

	def ParseArgs():
		global options, args

		parser = OptionParser()
		parser.add_option('-t', '--target', type='string', help='target for connection', dest='target', default=None)
		parser.add_option('-b', '--baud', dest='baud', type='int', help='baud rate for serial connection.', metavar='BAUD', default=19200)
		parser.add_option('-s', '--serialmode', dest='format', type='string', help='serial data format type. (Ascii or Binary)',  default='Ascii')
		parser.add_option('-l', '--log', dest='log', action='store_true', help='output log.', default=False)
		parser.add_option('-e', '--errormessage', dest='err', action='store_true', help='output error message.', default=False)
		(options, args) = parser.parse_args()

	if __name__ == '__main__':
		print("*** MONOWIRELESS App_PAL_Viewer " + Ver + " ***")

		ParseArgs()

		bEnableLog = options.log
		bEnableErrMsg = options.err
		try:
			PAL = AppPAL(port=options.target, baud=options.baud, tout=0.05, sformat=options.format, err=bEnableErrMsg)
		except:
			print("Cannot open \"AppPAL\" class...")
			exit(1)

		while True:
			try:
				# データがあるかどうかの確認
				if PAL.ReadSensorData():
					# あったら辞書を取得する
					Data = PAL.GetDataDict()
					if Data['RouterSID'] == '80000000':
						RSID = 'No Relay'
					else:
						RSID = Data['RouterSID']
					print(Data)
					print(Data['ArriveTime'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], end = ",")
					print(Data['LogicalID'], end = ",")
					print(Data['EndDeviceSID'], end = ",")
					print(RSID, end = ",")
					print(Data['SequenceNumber'], end = ",")
					print(Data['LQI'], end = ",")
					print(Data['Power'], end = "\n")
					datas_TAG = [str(Data['ArriveTime'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]),\
					Data['LogicalID'],Data['EndDeviceSID'],RSID,Data['SequenceNumber'],Data['LQI'],Data['Power']]

					csvout=csv.writer(f)

					csvout.writerow(datas_TAG)

					# なにか処理を記述する場合はこの下に書く
					#PAL.ShowSensorData()	# データを出力する
					# ここまでに処理を書く

					# ログを出力するオプションが有効だったらログを出力する。
					if bEnableLog == True:
						PAL.OutputCSV()	# CSVでログをとる

			# Ctrl+C でこのスクリプトを抜ける
			except KeyboardInterrupt:
				break

		del PAL

		print("*** Exit App_PAL Viewer ***")