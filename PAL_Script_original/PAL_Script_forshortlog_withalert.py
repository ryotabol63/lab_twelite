import csv
import serial
import serial.tools.list_ports
import sys
import datetime


#設定
baudrate = 38400  #ボーレートをMONOSTICKと同じ設定値にする
pidata = 'Nan'    #ラズパイによって設定値を変えて（番号とか）後々区別して処理できるようにする



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
            #いまのところMacは選別は非対応(実機ないので)
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

def sc16x4_2_int(hex):
    #符号付き16bitで保存されている値を符号を残してintにキャストする関数
    b = int(hex,16)  #16進数strをint型にキャスト
    return -(b & 0b1000000000000000) | (b& 0b0111111111111111)
#解説（備忘録）：(b & 0b1000000000000000)部分->正の数なら0負なら0b1000000000000000になる
#(b& 0b0111111111111111)は絶対値（補数）を抽出
# 式に-が入っていることでこのビット演算->整数化の過程は符号付intとして行われる
#※ふつうにやってしまうと、符号なしintとして整数化され不具合となる
# 検索ワード「符号つきバイナリ　int　python」
#あとは左結合でビット演算

class Tagdata:

    def __init__(self, tag_log, pidata):  #コンストラクタ
        self.nowtime = datetime.datetime.now()
        #受信時刻
        self.tag_id = tag_log[6:14]     #tag番号
        self.postnum = int(tag_log[28:32],16)   #送信連番
        self.lqi = int(tag_log[22:24], 16)    #電波強度
        #上二つはstr(16進数)->int->str(10進数)でキャストしている
        if len(tag_log) > 43: #加速度までちゃんと取れている
            self.acc_x_ave = sc16x4_2_int(tag_log[32:36])
            self.acc_y_ave = sc16x4_2_int(tag_log[36:40])
            self.acc_z_ave = sc16x4_2_int(tag_log[40:44])
        else:
            self.acc_x_ave = 'Nan'
            self.acc_y_ave = 'Nan'
            self.acc_z_ave = 'Nan'
        self.pidata = pidata
        

    def make_str_property_list(self):
        return ([self.nowtime.strftime('%Y%m%d_%H:%M:%S.%f')[:-3], self.tag_id, str(self.postnum), str(self.lqi),\
                 str(self.acc_x_ave), str(self.acc_y_ave), str(self.acc_z_ave), self.pidata])

    def write_to_csv(self, filename):
        #プロパティを指定されたcsvファイルに1行で書き込み
        self.str_property_list = self.make_str_property_list()
        with open(filename, 'a', newline='\n') as out_f:
            #データを書き込むときに逐一ファイルを開け閉めする
            out_f.write(','.join(self.str_property_list)+'\n')
            #書き込み



if __name__ == '__main__':
    ports = make_portlist()
    portnum = choose_port(ports)
    alertlist = []
    try:
        ser = serial.Serial(ports[portnum].device, baudrate= baudrate, timeout= 1.0)
        #シリアルポートインスタンスの定義（timeoutに設定された時間で下のtryループが回る->Ctrl+Cのキャッチ））
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
    header = ["time", "tag", "Number", "LQI", "xacc", "yacc", "zacc", "pidata","\n"]
    with open(filename, 'a', newline='\n') as out_f:
        out_f.write(','.join(header))


    #ここから値取得・書き込み
    try:
        while 1:
            #バイナリをデコードする
            line = ser.readline().decode('utf-8')
            if len(line) == 0:
                continue
            line = line.removeprefix(':')    #先頭の:を削除
            line_split = line.split(sep= ':')
            #取得データがつながってしまっている場合は":"で分割
            '''
            debugで使っていたが必要なさそうなので削除
            if len(line_split) == 1:        #つながっているデータを”：”で分割
                datatype_flag = 0               #分割が発生しない場合
            else: datatype_flag = 1             #分割が発生（電波強度は取れるが加速度欠損の可能性）

            '''
            
            for tag_log in line_split:
                print(len(tag_log))
                if len(tag_log) > 31 and tag_log[6:8] == '82':
                    #必要な情報が入っている最低の長さ and TWELITE_CUEからの正常受信
                    tagdata = Tagdata(tag_log, pidata)
                    if int(tagdata.postnum) < 3:
                        time_cut_index = 0
                        #ここから先あたりをMQTT受信先？？に組み込む
                        while (len(alertlist) > time_cut_index) and \
                            (alertlist[time_cut_index][0] < (tagdata.nowtime - datetime.timedelta(minutes = 20))):
                            time_cut_index += 1
                        alertlist = alertlist[time_cut_index:]
                        alertno = 0
                        for alert in alertlist:
                            if alert[1] == tagdata.tag_id:
                                alertno += 1
                            if alertno > 6:   #今回のを含めて再起動4回目以上と思われる
                                #アラート処理
                                break
                        alertlist.append((tagdata.nowtime, tagdata.tag_id))
                        print(alertlist)
                    tagdata.write_to_csv(filename)
            
                   
    except UnicodeDecodeError:
        #ごくまれにdecodeでエラーが起こる（その場合はpass）
        pass
    except KeyboardInterrupt:
        #ctrl+cで終了
        ser.close()
        print("finished")
        sys.exit(0)