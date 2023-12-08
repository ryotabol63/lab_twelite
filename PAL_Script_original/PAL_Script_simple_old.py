###このファイルは古い（新アプリに対応していない）ので注意！

import csv
import serial
import serial.tools.list_ports
import sys
import datetime

def make_portlist():
    #MONOSTICKが接続されていると思われるポート一覧を取得
    list = serial.tools.list_ports.comports()
    portlist_valid = []
    if sys.platform == 'win32':         #windows
        for p in list:
            if p.vid ==  1027 and p.pid == 24577 :
                #MONOSTICKに使われているvid,pidのみをポートリストに追加する
                portlist_valid.append(p)
    elif sys.platform == "linux":      #linux(linuxのほうが正確にMONOSTICKのみを抽出できる)
        for p in list:
            if 'MONOSTICK' in p.description:
                #MONOSTICKのみをポートリストに追加する
                portlist_valid.append(p)
        #print(str(p)[6:]) a
    else:
        for p in list:
            #いまのところMacは選別は非対応
            portlist_valid.append(p)
    #print(portlist_valid)
    return portlist_valid

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

class Tagdata:

    def __init__(self, log, datatype_flag):  #コンストラクタ
        self.nowtime = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-3]
        #受信時刻
        self.tag = log[14:22]     #tag番号
        self.postnum = str(int(log[10:14],16))   #送信連番
        self.lqi = int(log[8:10], 16)     #電波強度
        #上二つはstr(16進数)->int->str(10進数)でキャストしている
        self.datatypeflag = str(datatype_flag)
    
    def output_tagdata(self):
        pass
        






if __name__ == '__main__':
    ports = make_portlist()
    portnum = choose_port(ports)
    #ここからポート開く
    try:
        ser = serial.Serial(ports[portnum].device, baudrate= 38400)
        print(f"open {ports[portnum].device}")
    except:
        #開けなかった場合
        print(f"failed to open port{ports[portnum].device}")
        sys.exit(1)
        
    #保存ファイル名作成
    file_make_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "port_" + ports[portnum].device +"_" + file_make_time + ".csv" 
    print(filename)

    #ここから値取得・書き込み
    while 1:
            #データを書き込むときに逐一ファイルを開け閉めする
        try:
            #バイナリをデコードする
            line = ser.readline().decode('utf-8')
            #print(line)
            #取得データがつながってしまっている場合は":"で分割
            line_split = line.split(sep= ':')
            if len(line_split) == 2:        #つながっているデータを”：”で分割
                datatype_flag = 0               #データ分割処理をしていない=時刻情報も正しい
            else: datatype_flag = 1             #データ分割処理をしている=時刻情報は怪しい
            
            for log in line_split:
                print(len(log))
                if len(log) > 22:
                    #必要な情報(tag番号まで)が入っている最低の長さ
                    lqi = int(log[8:10], 16)    #電波強度
                    print(lqi)
                    postnum = int(log[10:14],16) #送信番号
                    tag = log[14:22]               #タグ番号
                    print(tag)
                    if tag[0:2] == '82':#MONOSTICKからのデータであることを判定
                        #データを処理した時間
                        #※要改善（つながってたデータを処理した場合、現状の時間は受信時刻ではなく、つながりを解消して書き込んだ時間）
                        nowtime= datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-3]
                        output_data = [nowtime, tag, str(postnum), str(lqi)]
                        
                        #debug(ファイル改変によって取れるようになったデータかどうかのフラグを付与する)
                        output_data.append(str(datatype_flag))

                        #各データごとに改行するための改行文字
                        output_data.append('\n')
                        with open(filename, 'a', newline='\n') as out_f:

                            out_f.write(','.join(output_data))
                            #書き込み
        except UnicodeDecodeError:
            #ごくまれにdecodeでエラーが起こる（その場合はpass）
            pass
        except KeyboardInterrupt:
            #ctrl+cで終了
            ser.close()
            print("finished")
            sys.exit(0)