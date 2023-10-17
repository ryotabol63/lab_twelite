import csv
import serial
import serial.tools.list_ports
import sys
import datetime


#設定
baudrate = 38400


def make_portlist():
    #MONOSTICKが接続されていると思われるポート一覧を取得
    list = serial.tools.list_ports.comports()
    portlist_valid = []
    for p in list:
        if 'USB Serial Port' in p.description:
            #シリアルポート≒MONOSTICKのみをポートリストに追加する
            portlist_valid.append(p)
        #print(str(p)[6:])
    #print(portlist_valid)
    return portlist_valid

def sc16x4_2_int(hex):
    b = int(hex,16)  #16進数strをint型にキャスト
    return -(b & 0b1000000000000000) | (b& 0b0111111111111111)
#解説（備忘録）：(b & 0b1000000000000000)部分->正の数なら0負なら0b1000000000000000になる
#(b& 0b0111111111111111)は絶対値を抽出
# 式に-が入っていることでこのビット演算->整数化の過程は符号付intとして行われる
#あとは左結合でビット演算


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
        ser = serial.Serial(ports[portnum].device, baudrate= baudrate, timeout= 1.0)
        print(f"open {ports[portnum].device}")
    except:
        #開けなかった場合
        print(f"failed to open port{ports[portnum].device}")
        sys.exit(1)
        
    #保存ファイル名作成
    file_make_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = "port_" + ports[portnum].device +"_" + file_make_time + ".csv" 
    print(filename)

    #ヘッダ書き込み
    header = ["time", "tag", "Number", "LQI", "xacc", "yacc", "zacc", "datatype", "\n"]
    with open(filename, 'a', newline='\n') as out_f:
        out_f.write(','.join(header))


    #ここから値取得・書き込み
    try:
        while 1:
            with open(filename, 'a', newline='\n') as out_f:
                #データを書き込むときに逐一ファイルを開け閉めする
                #バイナリをデコードする
                line = ser.readline().decode('utf-8')
                if len(line) == 0:
                    continue
                #print(line)
                #取得データがつながってしまっている場合は":"で分割
                line_split = line.split(sep= ':')
                if len(line_split) == 2:        #つながっているデータを”：”で分割
                    datatype_flag = 0               #もともとのPAL_Scriptでもとれるもの
                else: datatype_flag = 1             #今回の改変によって取れるようになったもの
                
                for tag_log in line_split:
                    print(len(tag_log))
                    if len(tag_log) > 31:
                        #必要な情報が入っている最低の長さ
                        lqi = int(tag_log[22:24], 16)    #電波強度
                        print(lqi)
                        postnum = int(tag_log[28:32],16) #送信番号
                        tag_id = tag_log[6:14]               #タグ番号
                        print(tag_id)
                        if tag_id[0:2] == '82':#MONOSTICKからのデータであることを判定
                            #データを処理した時間
                            #※要改善（つながってたデータを処理した場合、現状の時間は受信時刻ではなく、つながりを解消して書き込んだ時間）
                            nowtime= datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-3]
                            output_data = [nowtime, tag_id, str(postnum), str(lqi)]

                            if len(tag_log) > 43: #加速度までちゃんと取れている
                                acc_x_ave = sc16x4_2_int(tag_log[32:36])
                                acc_y_ave = sc16x4_2_int(tag_log[36:40])
                                acc_z_ave = sc16x4_2_int(tag_log[40:44])
                                #print((acc_x_ave,acc_y_ave,acc_z_ave))
                                output_data += [str(acc_x_ave), str(acc_y_ave), str(acc_z_ave)]

                            else:
                                output_data += ["Nan", "Nan", "Nan"]   #加速度をNaNでうめる（処理都合）  
                            
                            #debug(ファイル改変によって取れるようになったデータかどうかのフラグを付与する)
                            output_data.append(str(datatype_flag))

                            #各データごとに改行するための改行文字
                            output_data.append('\n')
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