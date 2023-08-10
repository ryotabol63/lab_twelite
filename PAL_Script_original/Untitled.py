# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import csv
import serial
import serial.tools.list_ports
import sys
import datetime
import csv


# %%
def make_portlist():
    list = serial.tools.list_ports.comports()
    portlist_valid = []
    for i in list:
        if 'USB Serial Port' in i.description:
            #シリアルポート≒MONOSTICKのみをポートリストに追加する
            portlist_valid.append(i)
        #print(str(i)[6:])
    #print(portlist_valid)
    return portlist_valid


# %%
#上の方をつかうことにします
def serial_ports():
    """ Lists serial port names
 
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
 
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# %%
#ports = serial_ports()
ports = make_portlist()
for i in range(len(ports)):
    print(f"{i}: {ports[i]}")
portnum = int(input())
if (portnum <0 or portnum > len(ports)):
    print("invalid portnum")


# %%
time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
print(time)
filename = "port_" + ports[portnum].device +"_" +  time + ".csv" 
print(filename)

# %%
ser = serial.Serial(ports[portnum].device, baudrate= 38400)

# %%
with open(filename, 'a') as out_f:
    while 1:
        try:
            line = ser.readline().decode('utf-8')
            #print(line)
            line_split = line.split(sep= ':')
            print(line_split)
            for log in line_split:
                print(len(log))
                if len(log) > 22:
                    lqi = int(log[8:10], 16)
                    print(log[8:10])
                    print(lqi)
                    tag = log[14:22]
                    print(tag)
                    if tag[0:2] == '82':#MONOSTICKからのデータであることを判定
                        nowtime= datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-3]
                        out_f.write(nowtime + '\n' + tag + ','+ str(lqi) + '\n')
        except UnicodeDecodeError:
            #ごくまれにdecodeでエラーが起こる（その場合はpass）
            pass
        except KeyboardInterrupt:
            ser.close()
            print("finished")
            break





# %%
ser.close()

# %%
aaa = 'aaa,aaa'
aaa.split(',')
aaa.split('i')

# %%
hoge = "800000007B1C8B820194F401808312113008020BCC1130010204D51504000600880000FC10150401060098FFF8FC20150402060088FFE0FC08150403060098FFF0FC001504040600A8FFF0FC081504050600880008FC08150406060090FF"
lqi = int(hoge[8:10], 16)

# %%
lqi

# %%
tag = hoge[14:22]

# %%
tag

# %%
nowtime= datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-3]

# %%
out_f.write(nowtime + '\n' + tag + ','+ str(lqi) + '\n')

# %%
with open('aaa.csv', 'a') as out_f:
    out_f.write(nowtime + '\n' + tag + ','+ str(lqi) + '\n')

# %%
print(int("E9",16))

# %%
aa = b'\af\ga\fate\x23\afa\efata\gae\2gs\g34\2342f'
line = aa.decode('utf-8')
print(line)

# %%
