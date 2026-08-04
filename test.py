import matplotlib.pyplot as plt
import numpy as np

x=np.linspace(-10,10,100)
y=x
y2=[i *2 for i in x]
plt.suptitle('Test graph1')
plt.subplot(2,1,1)
plt.plot(x,y,label='y=x',color='blue')

#formatting the graph
plt.xlabel('X axis')
plt.ylabel('Y axis')

plt.grid(True)


from matplotlib import font_manager,rc
font= 'C:/Windows/Fonts/Malgun.ttf'
font_name=font_manager.FontProperties(fname=font).get_name()
rc('font',family=font_name)

plt.suptitle("그래프")
plt.subplot(2,1,1)
plt.plot(x,y2,label='y=2x',color='blue')
plt.subplot(2,1,2)

#범례: 그래프 설명

plt.legend()


plt.show()