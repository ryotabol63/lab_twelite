import csv
import serial
import serial.tools.list_ports
import sys
import datetime

def make_portlist():
    #MONOSTICKが接続されていると思われるポート一覧を取得
    list = serial.tools.list_ports.comports()
    portlist_valid = []
    for i in list:
        if 'USB Serial Port' in i.description:
            #シリアルポート≒MONOSTICKのみをポートリストに追加する
            portlist_valid.append(i)
        #print(str(i)[6:])
    #print(portlist_valid)
    return portlist_valid

if __name__ == '__main__':
    ports = make_portlist()
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
    
    #ここからポート開く
    try:
        ser = serial.Serial(ports[portnum].device, baudrate= 38400)
        print(f"open {ports[portnum].device}")
    except:
        #開けなかった場合
        print(f"failed to open port{ports[portnum].device}")
        sys.exit(1)
        
    #保存ファイル名作成
    time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "port_" + ports[portnum].device +"_" +  time + ".csv" 
    print(filename)

    #ここから値取得・書き込み
    with open(filename, 'a') as out_f:
        while 1:
            try:
                line = ser.readline().decode('utf-8')
                #バイナリをデコードする
                #print(line)
                #取得データがつながってしまっている場合は":"で分割
                line_split = line.split(sep= ':')
                #print(line_split)
                
                for log in line_split:
                    print(len(log))
                    if len(log) > 22:
                        #必要な情報が入っている最低の長さ
                        lqi = int(log[8:10], 16)    #電波強度
                        print(lqi)
                        postnum = int(log[10:14],16) #送信番号
                        tag = log[14:22]               #タグ番号
                        print(tag)
                        if tag[0:2] == '82':#MONOSTICKからのデータであることを判定
                            nowtime= datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-3]
                            #データを処理した時間
                            #※要改善（つながってたデータを処理した場合、時間は受信時刻ではなく、つながりを解消して書き込んだ時間）
                            out_f.write(nowtime + ',' + tag + ',' + str(postnum) + ',' + str(lqi) + '\n')
                            #書き込み
            except UnicodeDecodeError:
                #ごくまれにdecodeでエラーが起こる（その場合はpass）
                pass
            except KeyboardInterrupt:
                #ctrl+cで終了
                ser.close()
                print("finished")
                sys.exit(0)