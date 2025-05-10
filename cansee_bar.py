import matplotlib.pyplot as plt
import numpy as np

x = np.arange(2020,2025)
y1 = np.array([60,60,58,53,76])
y2 = np.array([60,60,60,60,60])
bar_width = 0.3
plt.bar(x,y1,tick_label=["2020","2021","2022","2023","2024"],width=bar_width)
plt.bar(x,y2,bottom=y1,width=bar_width)
plt.show()
# x = np.arange(1,8)
# y = np.array([10770,16780,24440,30920,37670,48200,57270])
#
# plt.bar(x,y,tick_label=["FY2013","FY2014","FY2015","FY2016","FY2017","FY2018","FY2019"],width=0.5)

# x = np.arange(5)
# y1 = np.array([10,8,7,11,13])
# y2 = np.array([9,6,5,10,12])
# bar_width = 0.3

# plt.bar(x, y1, width=bar_width, tick_label=['a','b','c','d','e'],)
# plt.bar(x+bar_width, y2, width=bar_width)

# plt.bar(x, y1,  tick_label=['a','b','c','d','e'],width=bar_width,)
# plt.bar(x, y2, bottom=y1, width=bar_width)

# error = [2,1,2.5,2,1.5]
# plt.bar(x,y1,width=bar_width, tick_label=['a','b','c','d','e'],)
# plt.bar(x, y2, bottom=y1, width=bar_width, yerr=error)

