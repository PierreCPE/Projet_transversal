import json
import matplotlib.pyplot as plt
import math
import numpy as np
import time
import icp
import icp_git
# Opening JSON file
f = open('datav2.txt')
  
# returns JSON object as 
# a dictionary
datas = json.load(f)
  
# Closing file
f.close()
x_datas = []
y_datas = []
for scan in datas:
    x = np.zeros(len(scan))
    y = np.zeros(len(scan))
    for j,val in enumerate(scan):
        x[j] = (math.cos(val[1]*math.pi/180)*val[2])
        y[j] = (-math.sin(val[1]*math.pi/180)*val[2])
    x_datas.append(x)
    y_datas.append(y)

plt.ion()
figure, ax = plt.subplots(figsize=(8,6))

plt.xlabel("x",fontsize=18)
plt.ylabel("y",fontsize=18)

# for i in range(0,len(x_datas)-1):
for i in range(0,100):
    plt.cla()
    figure.suptitle(f"i={i}")
    x_max = 10000
    plt.xlim([-x_max, x_max])
    y_max = 10000
    plt.ylim([-y_max, y_max])
    ax.scatter(x_datas[i],y_datas[i], s=1, c=[[1,0,0]])
    ax.scatter(x_datas[i+1],y_datas[i+1], s=1, c=[[0,1,0]])
    data1 = np.array([x_datas[i],y_datas[i]]).T
    data2 = np.array([x_datas[i+1],y_datas[i+1]]).T
    
    theta = -np.radians(20)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    data2 = R.dot(data2.T).T + [100,200]
    # print(icp.icp(data1,data2))
    dt = icp.icp(data1,data2,figure,ax, amount = 100)
    #transformation_history, points = icp_git.icp(data1, data2, distance_threshold = 10, verbose=True)
    #print(transformation_history)
    # mean_data1 = np.mean(data1, axis=0)
    # for angle in np.linspace(6,7,360):
    #     plt.cla()
    #     ax.scatter(x_datas[0],y_datas[0], s=1, c=[[1,0,0]])
    #     ax.scatter(x_datas[i+1],y_datas[i+1], s=1, c=[[0,1,0]])
    #     theta = np.radians(angle)
    #     c, s = np.cos(theta), np.sin(theta)
    #     R = np.array(((c, -s), (s, c)))
    #     points = R.dot(data2.T).T
    #     links = {}
    #     for point in data2:
    #         cl = icp.closest(point,data1)
    #         if tuple(data1[cl]) in links:
    #             links[tuple(data1[cl])].append(point)
    #         else:
    #             links[tuple(data1[cl])] = [point]
    #     data1_selected = np.array(list(links.keys()))
    #     mean_data1_selected = np.mean(data1_selected, axis=0)
    #     print(len(data1_selected))
    #     print(mean_data1.shape)
    #     mean_points = np.mean(points, axis=0)
    #     print(points.shape)
    #     print(mean_points.shape)
    #     t = mean_data1_selected - mean_points
    #     points = points- t
    #     print(np.array(points).shape)
    #     ax.scatter(points.T[0],points.T[1], s=3, c=[[0,0,1]])
    #     figure.canvas.draw()
    #     figure.canvas.flush_events()
    # ax.scatter(dt[1][0],dt[1][1], s=3, c=[[0,1,1]])
    # ax.scatter(dt[2][0],dt[2][1], s=1, c=[[0.3,0.3,1]])
    time.sleep(1)
plt.pause(100)