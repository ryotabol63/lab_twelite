import csv
import os
import sys
from time import time
import numpy as np
from scipy import interpolate
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation
import random
import math
import pathlib
import operator
from matplotlib.animation import FuncAnimation


import kalman_for_tagdata

def maketaglist(csvname):
    with open (csvname, encoding = 'shift_jis')as ocsv:
        of = csv.reader(ocsv)
        next(of)  #ヘッダスキップ
        taglist = []
        for row in of:
                tagid = row[2]
                if not tagid in taglist:
                    taglist.append(tagid)
        return(taglist)

def partcsv (csvname,tagid):

    with open (csvname, encoding = 'shift_jis')as ocsv:
        of = csv.reader(ocsv)
        header = next(of)  #ヘッダ取得
        logname_parent = 'p_' + tagid+ '_From' + csvname
        changelogindex = []
        logno = 0
        index = 0
        with open(logname_parent,'w',encoding='shift_jis',newline='') as wf:
                    csvout = csv.writer(wf)
                    csvout.writerow(header)
        with open(logname_parent, 'a', encoding = 'shift-jis', newline = '')as af:
            firsttime = 0   #初期値
            for row in of:
                if firsttime ==0:
                    firsttime = row[0]
                lasttime = row[0]
                columnx = row[2]
                if columnx == tagid:
                    if logno > int(row[4]): #逆転が起こった場合
                        changelogindex.append(index)
                        logno = 0
                    else:
                        logno = int(row[4])
                    csvout = csv.writer(af)
                    csvout.writerow(row)
                    index += 1
        times = [firsttime, lasttime]
    changelogindex.append(index)
    print(changelogindex)
    lognames = []
    tagdata = pd.read_csv(logname_parent, encoding='shift-jis', dtype= 'object')
    data_from = 0
    current_logno = 1
    for data_to in changelogindex:
        if (data_to - data_from > 20): #小さいデータは除いてみる（是非は相談）
            logname = tagid + '_' + str(current_logno) + '_From' + csvname
            lognames.append(logname)
            #with open(logname,'w',encoding='shift_jis',newline='') as wf:
                        #csvout = csv.writer(wf)
                        #csvout.writerow(header)
            cur_tagdata = tagdata.loc[data_from:(data_to - 1)]
            print(cur_tagdata)
            cur_tagdata.to_csv(logname, encoding='shift-jis', mode= 'w', index=False)
            current_logno += 1
        data_from = data_to
    os.remove(logname_parent)
    return ((lognames,times))

def runpartcsv(taglist):
    tagdatalist = []
    timelist = []
    for tagid in taglist:
        run_part = partcsv(csvname, tagid)
        lognames = run_part[0]
        for log in lognames:
            tagdatalist.append(log)
        if timelist == []:
            timelist = run_part[1]
    return((tagdatalist,timelist))


def before_linear_withtagID (csvname):

    df = pd.read_csv(csvname, encoding='shift-jis',dtype= 'object')
    lognames = []
    pilist = df['piNo'].unique()
    for pino in pilist:
        logname = 'pi' + str(pino) + '_From' + csvname
        tagid = df.iat[1,2]     #行番号・列番号の順
        #print(tagid)
        header = list(df.columns.values)
        with open(logname,'w',encoding='shift_jis',newline='') as wf:      #前のデータが残っているといやなので上書き
            csvout = csv.writer(wf)
            header_for_write = [header[0], header[4], header[5], header[7], 'tagID:', tagid]
            csvout.writerow(header_for_write)
        data_by_pi = df.query('piNo == @pino')
        write_data = data_by_pi.iloc[:,[0, 4, 5, 7]]
        try:
            write_data.iloc[1]
            write_data.to_csv(logname, encoding='shift-jis', mode= 'a', header= False, index=False)
            lognames.append(logname)
            #複数列ないとエラー吐くので、、
        except:
            pass
    return(lognames)

def dmcsv_new(targetfile):

    savename = (os.path.splitext(targetfile)[0]) + '_linear.csv'


    #とりあえず間に合わせ（csvreadとwrite）でヘッダの処理はします（今後更新したい）
    with open (targetfile, encoding = 'shift_jis')as ocsv:
        of = csv.reader(ocsv)
        header = next(of)  #ヘッダスキップ
        #print(header)
    with open(savename,'w', encoding= 'shift-jis',newline = '') as f:
        header_write = csv.writer(f)
        header_write.writerow(header)

    get_time = np.loadtxt(targetfile, delimiter= ',', dtype= 'str', skiprows = 1, usecols=[0])
    num_lq = np.loadtxt(targetfile, delimiter=',', skiprows = 1, usecols=[1,2])
    try:
        pino = np.loadtxt(targetfile, delimiter=',', skiprows = 1, usecols=[3])[0]
    except:
        pino = np.loadtxt(targetfile, delimiter=',', skiprows = 1, usecols=[3])   #要素数1に対応、、苦しい。、
        out = np.stack([get_time,num_lq,linear_lq3f,pino_forcopy], 1)
    #print(num_lq)
    #print(len(get_time))
    #print(get_time[0])
    #print(get_time)
    #data = np.genfromtxt(targetfile, skip_header = 1, delimiter = ',', names=True, dtype= None, encoding = 'shift_jis')
    #print(data)
    #print(data[:,1])    #送信番号がある想定
    #print(data[:,2])    #電波強度



    #ddm = data[~np.isnan(data).any(axis = 1)]
    #get_time = ddm[:,0]
    get_time_ep = []
    for gt in get_time: #エポック秒に変換
        #print(gt)
        gt_dt = datetime.datetime.strptime(gt,'%Y/%m/%d %H:%M:%S.%f')      
        gt_ep = gt_dt.timestamp()
        get_time_ep.append(gt_ep)
    #print(get_time_ep)
    #print(len(get_time_ep))
    #num = ddm[:,1]
    num = num_lq[:,0]
    #lq = ddm[:,2]
    lq = num_lq[:,1]
    #print(num[0])
    min = num[0] 
    minnum = 0
    #このファイルでは探索で決まるようにする（逆転が起こる前）ので，基本的には書き換えられる
    max = num[-1]
    for i in range(len(num)-1):    #i番目とi+1番目を比較するのでlen-1
        if num [-(i+1)] <= num[-(i+2)]:    #逆転が起こっている
            min = num[-(i+1)]
            minnum = len(num) -(i+1)
            break
    #データ全体を切り取った配列を用意するtime_new,lq_new,num_new
    num_new = num[minnum:len(num)]
    get_time_ep_new = get_time_ep[minnum:len(num)]
    lq_new = lq[minnum:len(num)]
    numfixed = np.arange(min, max)
    #print(len(get_time_ep_new))
    #print(len(numfixed))

    #print(len(num))
    linear_lq = interpolate.interp1d(num_new,lq_new)  #num_new,#lq_new
    linear_tm = interpolate.interp1d(num_new,get_time_ep_new)
    #print(numfixed)
    linear_lq3f = np.round(linear_lq(numfixed),decimals = 2)
    linear_tmep = linear_tm(numfixed)
    pino_forcopy = []
    for i in range(len(linear_lq3f)):     #配列の長さをそろえてくっつけられるように
        pino_forcopy.append(int(pino))       
    linear_tm_dt = []
    for ltm in linear_tmep:
        ltm_dt = datetime.datetime.fromtimestamp(ltm)
        linear_tm_dt.append(ltm_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    #print(len(linear_lq3f))
    #print(len(pino_forcopy))
    out = np.stack([linear_tm_dt,numfixed,linear_lq3f,pino_forcopy], 1)
    #print(linear_lq3f)
    #print(numfixed.shape)
    #print(linear_lq3f.shape)
    #print(out)


    #print(type(ddm))

    #print(savename)
    with open(savename,'a',encoding= 'shift-jis') as f:
        fwrite = csv.writer(f, lineterminator='\n')
        fwrite.writerows(out)
    #np.savetxt(savename, out ,delimiter= ',', fmt=["%d","%.2f"])
    #print(type(out))
    return(savename)

def makeanimationlist(filelist):
    #とりあえず間に合わせ（csvreadとwrite）でヘッダの処理はします（今後更新したい）
    firstfile = filelist[0]
    savename = 'beforeanime_' + firstfile + '.csv'
    with open (firstfile, encoding = 'shift-jis')as ocsv:
        of = csv.reader(ocsv)
        header = next(of)  #ヘッダスキップ
        #print(header)
    tagid = header[5]
    with open(savename,'w', encoding= 'shift-jis',newline = '') as f:
        header_write = csv.writer(f)
        header_write.writerow(header)
    def_num = np.loadtxt(firstfile, delimiter=',', skiprows = 1, usecols=[1])
    num_min = def_num[0]
    num_max = def_num[-1]

    num_of_files = len(filelist)
    pinos = []
    datalist = []
    lqs = [] 
    for file in filelist:
        intdata = np.loadtxt(file, delimiter=',', skiprows = 1, usecols=[1,2,3])
        strdata = np.loadtxt(file, delimiter= ',', dtype='str', skiprows = 1, usecols=[0])
        #print(intdata.shape)
        strdata = strdata.reshape(len(strdata),1)
        #print(strdata.shape)
        data = np.block([strdata, intdata])
        datalist.append(data)
        if intdata[:,0][0] < num_min:
            num_min = intdata[:,0][0]
        if intdata[:,0][-1] > num_max:
            num_max = intdata[:,0][-1]
    #print(datalist)
    out = []
    for i in range(int(num_min),int(num_max+1)):
        maxlq = 0
        for d in datalist:
            nums = []
            #print(d[:,1])
            for k in d[:,1]:
                #print(k)
                nums.append(int(float(k)))
            if i in nums:
                x = nums.index(i)
                #print(d[x][2])
                if float(d[x][2]) > maxlq:
                    maxlq = float(d[x][2])
                    data_for_out = d[x]
        if maxlq != 0:
            out.append(data_for_out)
    #print(out)
    with open(savename,'a',encoding= 'shift-jis') as f:
        fwrite = csv.writer(f, lineterminator='\n')
        fwrite.writerows(out)
    return(savename)

def prepareforanime_yamaguchi(tgtfile):
    with open (tgtfile, encoding = 'shift-jis')as ocsv:
        of = csv.reader(ocsv)
        old_header = next(of)  #ヘッダスキップ
    tagid = old_header[5]
    timedata = np.loadtxt(tgtfile, delimiter= ',', dtype='str', skiprows = 1, usecols=[0])
    pidata = np.loadtxt(tgtfile, delimiter= ',', skiprows = 1, usecols=[3])
    timedata_dt = []
    for tm in timedata:
        #print(tm)
        #print(type(tm))
        try:
            tm_dt = datetime.datetime.strptime(tm,'%Y-%m-%d %H:%M:%S.%f')
            timedata_dt.append(tm_dt)
        except ValueError:
            pass
    #print(timedata_dt)
    #print(len(timedata_dt))
    #print(pidata)
    pidata_int = []
    for pi in pidata:
        pidata_int.append(int(pi))
    curdata = 0                 #今はどのデータまでチェックできたか
    timeslice = 0               #開始時から何秒経過したか
    datalen = len(timedata_dt)
    memo = '0'                        #初期値はこうすることとします（プロットを工夫して）
    curtimemin = timedata_dt[0]
    sec = int(curtimemin.second)
    #print(sec)
    if sec % 2 != 0:     #奇数秒なので
        curtimemin = curtimemin.replace(second = (sec - 1))
    curtimemin = curtimemin.replace(microsecond= 0)
    timedif = 2
    curtimemax = curtimemin + datetime.timedelta(seconds = float(timedif))
    timelist = []
    while curdata < datalen and curtimemax <= timedata_dt[-1]:
        if timedata_dt[curdata] < curtimemin:
            curdata = curdata + 1 #実験開始時刻までのデータはカット
            continue
        elif curtimemin <= timedata_dt[curdata] and timedata_dt[curdata] < curtimemax:
            memo = pidata[curdata]
            curdata = curdata + 1
            #print(curdata)
        timelist.append([curtimemin.strftime('%Y-%m-%d %H:%M:%S'), memo, tagid])
        curtimemin = curtimemax
        curtimemax = curtimemin + datetime.timedelta(seconds = float(timedif))                       #やばかったらここを変えよう（2までは許容！）
            #変える場合はanimation の方の秒数も変える必要あり、変数化したい
        timeslice += timedif
    #print(timelist)
    starttime_str = timedata_dt[0].strftime('%Y%m%d%H%M%S')
    stoptime_str = timedata_dt[-1].strftime('%Y%m%d%H%M%S')

    savename = tagid + '_' + starttime_str + '_' + stoptime_str + '.csv'
    with open(savename,'w', newline='') as f:
        writer = csv.writer(f)
        header =[tagid,'starttime:', starttime_str, 'stoptime:', stoptime_str]
        writer.writerow(header)
        for data in timelist: 
            writer.writerow(data)
    return(savename)



def sort_csv(csv_file: pathlib, sort_row: int, desc: bool = False):
    '''
    第一引数：編集するCSVファイルをフルパスで指定
    第二引数：ソートする列を数字で指定(左から0,1,2・・・)
    第三引数：昇順(False)降順(True)を指定
    '''
    # 今回作成したuser_list_csvを開く
    csv_data = csv.reader(open(csv_file), delimiter=',')
    # ヘッダー情報を取得
    header = next(csv_data)
    # ヘッダー以外の列を並び替える
    sort_result = sorted(csv_data, reverse=desc, key=operator.itemgetter(sort_row))

    # 新規ファイルとしてuser_list_csvを開く
    with open(csv_file, "w", newline='') as f:
        # ヘッダーと並び替え結果をファイルに書き込む
        data = csv.writer(f, delimiter=',')
        data.writerow(header)
        for r in sort_result:
            data.writerow(r)

def unitcsv(files):
    savename = 'alltagdata.csv'
    alltag_data = []
    for file in files:
        csv_data = csv.reader(open(file), delimiter=',')
        header = next(csv_data)
        for row in csv_data:
            #row[0] = datetime.datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S')
            alltag_data.append(row)
    pd_alltag_data = pd.DataFrame(alltag_data, columns=['time','pino','tagid'])
    pd_alltag_data["time"] = pd.to_datetime(pd_alltag_data["time"])
    #print(pd_alltag_data['time'])
    pd_alltag_data.sort_values('time', inplace= True)
    pd_alltag_data.to_csv(savename, index= False)
    return(savename)
    


        
        
    
#############drawanime

def determine_coordinate():
    coordinate = []   #座標
    pi1 = (2,2)         #pi1(x,y)
    pi2 = (6,2)         #pi2(x,y)
    pi3 = (9,1)         #pi3(x,y)
    pi4 = (12,8)         #pi4(x,y)    
    pi5 = (15,6)         #pi5(x,y)
    pi6 = (-10,-10)         #pi6(x,y)
    coordinate.extend([pi1,pi2,pi3,pi4,pi5,pi6])
    #print(coordinate)
    return(coordinate)


def coordinate(pn,coordinatexy):     #ここで座標を入力
    if pn >= 1 and pn <= 6:
        x = coordinatexy[(int(pn)-1)][0]
        y = coordinatexy[(int(pn)-1)][1]
    else:
        x = 0
        y = 0
    return (x,y)

'''

def animetest(dataset_for_anime, times):

    firsttime = datetime.datetime.strptime(times[0],'%Y/%m/%d %H:%M:%S.%f')[:-3]
    firsttime.replace(microsecond= 0)
    lasttime = datetime.datetime.strptime(times[1],'%Y/%m/%d %H:%M:%S.%f')[:-3]

    fig = plt.figure()
    #print(type(targetfile))
    
    anim = [] #アニメーション用に描くパラパラ図のデータを格納するためのリスト
    data = []
    for target in dataset_for_anime[0]: #データ取り込み部
        data.append(np.genfromtxt(target, skip_header = 1, delimiter = ',', encoding = 'utf-8'))#ヘッダ１行
    #t = data[0][:,0].tolist()
    #tt = [int(k) for k in t]

    #この状態で各csvからデータを読み取り終わっている

    #各データに対する描画用乱数設定

    #ここからアニメーション描画
    slice = 2  #アニメーション一枚の間隔
    curtime = firsttime
    while curtime < lasttime:
        for i in range(len(dataset_for_anime)):
            #if 


        curtime + datetime.timedelta(seconds = float(slice))


    
    ylist = []
    xrand = []
    yrand = []
    #print(data)
    count = 0
    for list in data:
        count += 1
        #print(data[:,0])
        #print(tt)
        theta = 2.0 * math.pi * random.random()
        radius = math.sqrt(random.random())
        xrand.append(0.2 * radius * math.cos(theta))
        yrand.append(0.2 * radius * math.sin(theta))
        ylist.append(list[:,1].tolist())
    #print(xrand)
    #print(yrand)
    #print(count)

    #print (type(y))
    phistory = [0, 0, 0, 0, 0, 0]     #各pi を踏んだ回数
    coordinatexy = determine_coordinate()   #xy座標の定義

    tryno = 0
    for j in tt:
        curdatetime = basedatetime + datetime.timedelta(seconds= j)
        curtime = curdatetime.strftime('%H:%M:%S')
        im = plt.plot()
        #print(type(im))
        counter = 0
        #print(ylist)
        jind = tt.index(j)
        for pllist in ylist:
            #print(pllist)
            try:
                cpl = pllist[jind]
                phistory[(int(cpl)- 1)] += 1 
                co = coordinate(cpl,coordinatexy)
                x = co[0] + xrand[counter]
                #print(x)
                y = co[1] + yrand[counter]
                im = im + plt.plot(x,y,'s', color='red',markersize=5, aa=True)
            except IndexError:
                pass
            counter += 1
        tryno += 1
        #sum_phis = sum(phistory)
        p_rate = [0,0,0,0,0,0]
        if tryno != 0:
            for i in range(6):
                p_rate[i] = phistory[i] / tryno
        #print(p_rate)
        his_text = 'P1:' + str(phistory[0]) + 'times, ' + str(round(p_rate[0] * 100)) + '%\n' + \
                   'P2:' + str(phistory[1]) + 'times, ' + str(round(p_rate[1] * 100)) + '%\n' + \
                   'P3:' + str(phistory[2]) + 'times, ' + str(round(p_rate[2] * 100)) + '%\n' + \
                   'P4:' + str(phistory[3]) + 'times, ' + str(round(p_rate[3] * 100)) + '%\n' + \
                   'P5:' + str(phistory[4]) + 'times, ' + str(round(p_rate[4] * 100)) + '%\n' + \
                   'P6:' + str(phistory[5]) + 'times, ' + str(round(p_rate[5] * 100)) + '%\n'
        #print(his_text)
        tx = plt.text(12,10,curtime + '\n' + his_text)       #時間のprintはここ
        anim.append(im + [tx])
    
    anim = ArtistAnimation(fig, anim) # アニメーション作成
    
    #円とラベルの描画
    N = 200 #曲線のなめらかさ
    pi_2 = 2.0 * math.pi
    t = np.linspace(0,pi_2,N)#媒介変数
    #centerlistx = (13,1,5,3,8)#円の中心リスト（各Piの位置に相当）
    #centerlisty = (5,8,8,2,1)
    for num in range(0,6):
        cirx = coordinatexy[num][0] + 0.5 * np.cos(t)
        ciry = coordinatexy[num][1] + 0.5 * np.sin(t)
        plt.plot(cirx,ciry,'-', color='blue')
        piname = 'P' + str(num + 1)
        plt.text(coordinatexy[num][0]-1.2, coordinatexy[num][1]+0.4, piname)
    r1x = np.linspace(0,10,N)
    #r2x = np.linspace(10,16,N)
    ry = np.linspace(1,9,100)
    for xn in (12,15):
        rrx = np.linspace(xn,xn,100)
        plt.plot(rrx,ry,color= 'black')
    for yn in (2,-100):
        rry = np.linspace(yn,yn,N)
        plt.plot(r1x,rry,color= 'black')
        #plt.plot(r2x,rry,color = 'black')
    plt.text(3,3,'Zipline')
    plt.text(12,5,'Slacklines')
    plt.text(4,6,'Athletics')
    #plt.xlabel('X',fontsize=18)
    #plt.ylabel('Y',fontsize=18)
    plt.xlim(0,18)              #描画領域(x)
    plt.ylim(0,16)              #描画領域(y)

    fig.show() 
    savename = 'animetest.gif'
    anim.save(savename, writer='pillow')   #アニメーションをt.gifという名前で保存し，gifアニメーションファイルを作成する。
    return(savename)

'''

def animation_write():





    used_pinm = 5  #今回使用したラズパイの数


    with open ('alltagdata.csv', encoding = 'utf-8')as ocsv:
        row = csv.reader(ocsv)
        header = next(row)  #ヘッダスキップ
        location_datas = [s for s in row]
    #print(location_data)
    cur_time = location_datas[0][0]
    print(cur_time)
    location_list = [0 for i in range(used_pinm)]
    print(location_list)
    location_by_time = []
    for location in location_datas:
        if not location[0] == cur_time:
            #print(cur_time,location_list)
            location_by_time.append([cur_time,location_list])
            cur_time = location[0]
            location_list = [0 for i in range(used_pinm)]
        pino = int(float(location[1])) - 1
        #print(pino)
        location_list[pino] += 1
    print(location_by_time)

    fig = plt.figure()
    plt.subplot(111)

    coordinatexy = determine_coordinate()   #xy座標の定義

    #円とラベルの描画
    N = 200 #曲線のなめらかさ
    pi_2 = 2.0 * math.pi
    t = np.linspace(0,pi_2,N)#媒介変数
    #centerlistx = (13,1,5,3,8)#円の中心リスト（各Piの位置に相当）
    #centerlisty = (5,8,8,2,1)

    for num in range(0,used_pinm):
        cirx = coordinatexy[num][0] + 1.0 * np.cos(t)
        ciry = coordinatexy[num][1] + 1.0 * np.sin(t)
        plt.plot(cirx,ciry,'-', color='blue')
        piname = 'P' + str(num + 1)
        plt.text(coordinatexy[num][0]-1.2, coordinatexy[num][1]+0.4, piname)

    r1x = np.linspace(0,10,N)
    #r2x = np.linspace(10,16,N)
    ry = np.linspace(1,9,100)
    for xn in (12,15):
        rrx = np.linspace(xn,xn,100)
        plt.plot(rrx,ry,color= 'black')
    for yn in (2,-100):
        rry = np.linspace(yn,yn,N)
        plt.plot(r1x,rry,color= 'black')
        #plt.plot(r2x,rry,color = 'black')
    plt.text(3,3,'Zipline')
    plt.text(12,5,'Slacklines')
    plt.text(4,6,'Athletics')
    #plt.xlabel('X',fontsize=18)
    #plt.ylabel('Y',fontsize=18)
    plt.xlim(0,18)              #描画領域(x)
    plt.ylim(0,16)              #描画領域(y)
    p = []

    xrand = []
    yrand = []
    for i in range(used_pinm):
        xa = []
        ya = []
        for n in range(50):
            theta = 2.0 * math.pi * random.random()
            radius = math.sqrt(random.random())
            xa.append(0.8 * radius * math.cos(theta))
            ya.append(0.8 * radius * math.sin(theta))
        xrand.append(xa)
        yrand.append(ya)


    print(coordinatexy)
    def update(frame):
        while p != []:
            print(p)
            print(len(p))
            rem = p.pop(0)
            rem.remove()
        print(p)
        #print(frame[0])
        p.append(plt.text(12,14, frame[0]))
        plt_x = []
        plt_y = []
        picount = 0
        for item in frame[1]:
            if not item == 0:
                for i in range(item):
                    #print(coordinatexy[picount][0] + xrand)
                    plt_x.append(coordinatexy[picount][0] + xrand[picount][i])
                    plt_y.append(coordinatexy[picount][1] + yrand[picount][i])
            picount += 1
        if plt_x != []:
            print(plt_x)
            p.extend(plt.plot(plt_x, plt_y, 's', color='red',markersize=5, aa=True))   #pltplotはリストなのでextend
            


    anim = FuncAnimation(fig, update, frames = location_by_time, interval = 500)
    #plt.show()
    anim.save('test1.gif', writer= 'pillow')
    #anim.save('anim.mp4', writer="ffmpeg")
    plt.close



if __name__ == '__main__':
    csvname = input('filename:')
    focused_tagid  = input('tagid(下4桁【ALL TAG->0入力】):')
    print('partcsv')
    if focused_tagid == '0':
        tagid_list =  maketaglist(csvname)
    else:
        tagid_list = [('8201' + focused_tagid)]
    tagdatalist_times = runpartcsv(tagid_list)
    tagdatalist = tagdatalist_times[0]
    times = tagdatalist_times[1]
    #print(tagdatalist)     #各タグiDごと、切れ目ごとにファイルが生成される
    #tagid = '8201' + input('tagID(下4桁):')
    #b = int(input('columnno:'))
    #c = int(sys.argv[3])
    print('1st_process')
    tag_pi_datalist = []
    for file in tagdatalist:
        lognames = before_linear_withtagID(file)
        tag_pi_datalist.append(lognames)      #[[tagdatalistをpiごとに分割][]]の2次元配列
    #print(tag_pi_datalist)
    linear_file_names = []
    print('2nd_process(linear)')
    for tag_datalist in tag_pi_datalist:
        linear_files_by_pi = []
        for file in tag_datalist:
            linearname =  dmcsv_new(file)
            linear_files_by_pi.append(linearname)
        linear_file_names.append(linear_files_by_pi)
        #lognames->linear_files_by_pi
        #tag_pi_datalist->linear_file_names
    kalman_file_names = []
    print('3rd_process(kalman)')
    for tag_datalist_linear in linear_file_names:
        kalman_files_by_pi = []
        for file in tag_datalist_linear:
            kalman_file = kalman_for_tagdata.kalman_for_tagdata(file,2)
            kalman_files_by_pi.append(kalman_file)
        kalman_file_names.append(kalman_files_by_pi)
    #print(kalman_file_names)
    print('4th_process(prepare_for_anime)')
    animelist = []
    for kalman_filelist in kalman_file_names:
        animename = makeanimationlist(kalman_filelist)
        animelist.append(animename)
    print('final_process(animation)')
    files_for_anime = []
    for dataforanime in animelist:
        args_foranime = prepareforanime_yamaguchi(dataforanime)
        files_for_anime.append(args_foranime)
    print(files_for_anime)
    alldata_for_anime = unitcsv(files_for_anime)

    used_pinm = 5  #今回使用したラズパイの数


with open ('alltagdata.csv', encoding = 'utf-8')as ocsv:
    row = csv.reader(ocsv)
    header = next(row)  #ヘッダスキップ
    location_datas = [s for s in row]
#print(location_data)
cur_time = location_datas[0][0]
print(cur_time)
location_list = [0 for i in range(used_pinm)]
print(location_list)
location_by_time = []
for location in location_datas:
    if location[0] == cur_time:
        pino = int(float(location[1])) - 1
        #print(pino)
        location_list[pino] += 1
    else:
        #print(cur_time,location_list)
        location_by_time.append([cur_time,location_list])
        cur_time = location[0]
        location_list = [0 for i in range(used_pinm)]
        pino = int(float(location[1])) - 1
        #print(pino)
        location_list[pino] += 1
print(location_by_time)
animation_write()

    #final_savename = animetest(dataset_for_anime, times)
    #print('Finished. File name is "' + final_savename + '"')