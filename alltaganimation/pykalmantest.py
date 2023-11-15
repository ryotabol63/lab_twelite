import pykalman
import matplotlib.pyplot as plt
import numpy as np


####################カルマンフィルタ(unscented kalman filter)(cが小さい程強くかかります)#####################


x = [i for i in range(100)]     #１０の倍数で指定すること(１０で割ってます)
#print(x)
#prepareing y 

y = np.array([2 for i in x])
noise1_size = len(x)//10
for_noise1 = np.random.normal(loc= 0, scale = 0.5, size = noise1_size)
for_noise1_2 = np.random.normal(loc= 0, scale = 0.5, size = noise1_size)
noise1 = np.array([for_noise1[i] for i in range(noise1_size) for k in range(10)])
noise1_2 = np.array([for_noise1_2[i] for i in range(noise1_size) for k in range(10)])
#print(noise1)
noise2 = np.random.normal(loc= 0, scale= 0.2, size = len(x))
noise2_2 = np.random.normal(loc= 0, scale= 0.2, size = len(x))
#print(len(noise1))
#print(len(noise2))
#print(type(y))
#print(type(noise2))
#y = 
testdata = y + noise1 + noise2
testdata_2 = y + noise1_2 + noise2_2
ideal = y + noise1
ideal_2 = y + noise1_2


############c = 1################

coverrianceA = 1

ukf = pykalman.UnscentedKalmanFilter(initial_state_mean= testdata[0], initial_state_covariance= testdata[0]/10,transition_covariance= coverrianceA)
ukf_2 = pykalman.UnscentedKalmanFilter(initial_state_mean= testdata_2[0], initial_state_covariance= testdata_2[0]/10,transition_covariance= coverrianceA)
filtered = ukf.filter(testdata)
smoothed = ukf.smooth(testdata)
filtered_2 = ukf_2.filter(testdata_2)
smoothed_2 = ukf_2.smooth(testdata_2)

bigf = (filtered[0])
bigs = (smoothed[0])
bigf_2 = (filtered_2[0])
bigs_2 = (smoothed_2[0])



#############c = 0.3###############
coverrianceB = 0.3

ukf = pykalman.UnscentedKalmanFilter(initial_state_mean= testdata[0], initial_state_covariance= testdata[0]/10,transition_covariance= coverrianceB)
ukf_2 = pykalman.UnscentedKalmanFilter(initial_state_mean= testdata[0], initial_state_covariance= testdata[0]/10,transition_covariance= coverrianceB)
filtered = ukf.filter(testdata)
smoothed = ukf.smooth(testdata)
filtered_2 = ukf_2.filter(testdata_2)
smoothed_2 = ukf_2.smooth(testdata_2)

smallf = (filtered[0])
smalls = (smoothed[0])
smallf_2 = (filtered_2[0])
smalls_2 = (smoothed_2[0])




x = []
for i in range(len(testdata)):
    x.append(i)
    print(testdata[i],smallf[i],bigf[i],smalls[i],bigs[i])

fig = plt.figure()

plt.subplot(221)

plt.plot(x,testdata,color= 'red', label= 'original')
plt.plot(x,ideal,color= 'black', label= 'ideal')
plt.plot(x,testdata_2,color= 'gray', label= 'original_2')
plt.plot(x,ideal_2,color= 'purple', label= 'ideal_2')
#plt.plot(x,smalls,color= 'blue', label= 'smoothed c=0.3')
plt.plot(x,y,color = 'green', label= '--')
plt.legend()

plt.subplot(222)

#plt.plot(x,testdata,color= 'black', label= 'original')
plt.plot(x,ideal,color= 'black', label= 'ideal')
plt.plot(x,bigf,color= 'red', label= 'filtered c={}'.format(coverrianceA))
plt.plot(x,bigs,color= 'blue', label= 'smoothed c={}'.format(coverrianceA))
plt.plot(x,y,color = 'green', label= '--')
plt.legend()

plt.subplot(223)

#plt.plot(x,testdata,color= 'black', label= 'original')
plt.plot(x,ideal,color= 'black', label= 'ideal')
plt.plot(x,ideal_2,color= 'purple', label= 'ideal_2')
plt.plot(x,bigf,color= 'red', label= 'filtered c={}'.format(coverrianceA))
plt.plot(x,bigf_2,color= 'blue', label= 'filtered_2 c={}'.format(coverrianceA))
plt.plot(x,y,color = 'green', label= '--')
plt.legend()


plt.subplot(224)
#plt.plot(x,testdata,color= 'black', label= 'original')
plt.plot(x,ideal,color= 'black', label= 'ideal')
plt.plot(x,ideal_2,color= 'purple', label= 'ideal_2')
plt.plot(x,smallf,color= 'red', label= 'filtered c={}'.format(coverrianceB))
plt.plot(x,smallf_2,color= 'blue', label= 'filtered_2 c={}'.format(coverrianceB))
plt.plot(x,y,color = 'green', label= '--')
plt.legend()




plt.show()