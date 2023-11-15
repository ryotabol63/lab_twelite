import matplotlib.pyplot as plt
#import pandas
import numpy as np
#from matplotlib.animation import ArtistAnimation
from matplotlib.animation import FuncAnimation
import os
import random
import math
import datetime
import matplotlib.patches as patches
import csv

def determine_coordinate():
    coordinate = []   #座標
    pi1 = (2,2)         #pi1(x,y)
    pi2 = (6,2)         #pi2(x,y)
    pi3 = (9,1)         #pi3(x,y)
    pi4 = (12,8)         #pi4(x,y)    
    pi5 = (15,6)         #pi5(x,y)
    pi6 = (-16,-19)         #pi6(x,y)
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


#########################実装時は消す###########################
with open ('alltagdata.csv', encoding = 'shift_jis')as ocsv:
    of = csv.reader(ocsv)
    next(of)  #ヘッダスキップ
    taglist = []
    for row in of:
            tagid = row[2]
            if not tagid in taglist:
                taglist.append(tagid)

##############################################################

tagrand = []
for tag in taglist:
    theta = 2.0 * math.pi * random.random()
    radius = math.sqrt(random.random())
    xrand = 0.8 * radius * math.cos(theta)
    yrand = 0.8 * radius * math.sin(theta)
    tagrand.append((xrand, yrand))

print(tagrand)        #taglistの順番と対応している

    

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
location_by_tag = [-1 for i in range(len(taglist))]
changecounter = 0

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
location_list =[]
change_list = []

for location in location_datas:
    if not location[0] == cur_time:
        #前の時間のデータを保存
        location_by_time.append([cur_time,location_list,change_list])
        cur_time = location[0]
        location_list = []
        change_list = []


    pino = int(float(location[1])) - 1
    cur_tagid = location[2]
    tag_index = taglist.index(cur_tagid)
    prev_location = location_by_tag[tag_index]
    if (prev_location >=0) and (prev_location != pino):
        #位置の移動がある場合(矢羽根を書きたい)
        change_list.append([cur_tagid, prev_location, pino])
        #タグID,前の場所,移動先
        print('change')
        
    location_by_tag[tag_index] = pino
    #print(pino)
    location_list.append([cur_tagid,pino])
#print(location_by_time)

'''

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
'''
p = []

#print(coordinatexy)
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
    for printtag in frame[1]:    #タグの場所の描画
        tag_index = taglist.index(printtag[0])
        cur_rand = tagrand[tag_index]
        plt_x.append(coordinatexy[printtag[1]][0] + cur_rand[0])
        plt_y.append(coordinatexy[printtag[1]][1] + cur_rand[1])
    if plt_x != []:
        print(plt_x)
        p.extend(plt.plot(plt_x, plt_y, 's', color='red',markersize=5, aa=True))   #pltplotはリストなのでextend

    for changetag in frame[2]:
        tag_index = taglist.index(changetag[0])
        cur_rand = tagrand[tag_index]
        x_changeloc = [coordinatexy[changetag[1]][0] + cur_rand[0], coordinatexy[changetag[2]][0] + cur_rand[0]]
        y_changeloc = [coordinatexy[changetag[1]][1] + cur_rand[1], coordinatexy[changetag[2]][1] + cur_rand[1]]
        p.extend(plt.plot(x_changeloc, y_changeloc, color= 'blue', lw = 1))
        

    
        


anim = FuncAnimation(fig, update, frames = location_by_time, interval = 500)
#plt.show()
anim.save('test1.gif', writer= 'pillow')
#anim.save('anim.mp4', writer="ffmpeg")
plt.close
print(tagrand)
print(changecounter)