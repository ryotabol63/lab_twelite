#シリアルで読み取ったものをそのまま垂れ流すスクリプト（debag用）

import csv
import serial
import serial.tools.list_ports
import sys
import datetime


def make_portlist():
    #MONOSTICKが接続されていると思われるポート一覧を取得
    list = serial.tools.list_ports.comports()
    portlist= []
    for p in list:
        portlist.append(p)

    return portlist

def choose_port(ports):
    #ポートリストをprint
    for i in range(len(ports)):
        print(f"{i}: {ports[i]}")
    validport = False #初期値
    while validport == False:
        #正しい値が入力されるまでループ
        print("input portnum->",end= '')
        try:
            portnum = int(input())
        except KeyboardInterrupt:
            print("aborted")
            sys.exit(1)
        except:
            print("could not cast to int please input number")
            continue
        if (portnum <0 or portnum > (len(ports)-1) ):
            print("invalid portnum")
        else:
            validport = True

    return portnum


        


if __name__ == '__main__':
    ports = make_portlist()
    portnum = choose_port(ports)
    baudrate = int(input('baudrate?: '))
    log = int(input('log[1->True, 0->False]?: '))
    try:
        ser = serial.Serial(ports[portnum].device, baudrate= baudrate, timeout= 1.0)
        #シリアルポートインスタンスの定義（timeoutに設定された時間で下のtryループが回る->Ctrl+Cのキャッチ））
        print(f"open {ports[portnum].device}")
    except:
        #開けなかった場合
        print(f"failed to open port{ports[portnum].device}")
        sys.exit(1)
    
    if log:
    #保存ファイル名作成
        file_make_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "serialread_port_" + ports[portnum].device +"_" + file_make_time + ".csv" 
        print(filename)


    #ここから値取得・書き込み
    try:
        while 1:
            #バイナリをデコードする
            line = ser.readline().decode('utf-8')
            nowtime = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-3]
            if len(line) == 0:
                continue
            print(nowtime)
            print(line)
            if log:
                with open(filename, 'a', newline='\n') as out_f:
                    #データを書き込むときに逐一ファイルを開け閉めする
                    out_f.write(','.join([nowtime,line]))
                    #書き込み
          
    except UnicodeDecodeError:
        #ごくまれにdecodeでエラーが起こる（その場合はpass）
        pass
    except KeyboardInterrupt:
        #ctrl+cで終了
        ser.close()
        print("finished")
        sys.exit(0)