import matplotlib.pyplot as plt
from scipy.fftpack import fft
import numpy as np
import openpyxl
import sys
import random
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        # self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改
        # self.axes.cla()  # 每次绘图的时候不保留上一次绘图的结果

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # 绘制图形
    def start_static_plot(self):
        data = pd.read_excel("数据1.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y1 = []
        for i in lie:
            y1.append(i[0])
        data = pd.read_excel("数据2.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y2 = []
        for i in lie:
            y2.append(i[0]+1)
        data = pd.read_excel("数据3.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y3 = []
        for i in lie:
            y3.append(i[0]+2)
        data = pd.read_excel("数据4.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y4 = []
        for i in lie:
            y4.append(i[0]+3)
        x = []
        for j in range(0, 60):
            x.append(j)

        ax = self.figure.add_subplot(221)
        ax.plot(x[0:60], y1[0:60], label='时域1')
        ax.plot(x[0:60], y2[0:60], label='时域2')
        ax.plot(x[0:60], y3[0:60], label='时域3')
        ax.plot(x[0:60], y4[0:60], label='时域4')
        ax.legend()
        ax.set_title('时域图')
        ax.set_ylabel('幅值')

        data = pd.read_excel("应力数据.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y9 = []
        for i in lie:
            y9.append(i[0])
        bx = self.figure.add_subplot(222)
        bx.plot(x, y9, 'r')
        bx.set_title('应力图')
        bx.set_xlabel('时间(s)')
        bx.set_ylabel('应力值')

        data = pd.read_excel("倾角1.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y10 = []
        for i in lie:
            y10.append(i[0])
        data = pd.read_excel("倾角2.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y11 = []
        for i in lie:
            y11.append(i[0]+1)
        data = pd.read_excel("倾角3.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y12 = []
        for i in lie:
            y12.append(i[0]+2)
        data = pd.read_excel("倾角4.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        y13 = []
        for i in lie:
            y13.append(i[0]+3)

        cx = self.figure.add_subplot(223)
        cx.plot(x, y10, label='倾角1')
        cx.plot(x, y11, label='倾角2')
        cx.plot(x, y12, label='倾角3')
        cx.plot(x, y13, label='倾角4')
        cx.legend()
        cx.set_title('倾角')
        cx.set_xlabel('时间(s)')
        cx.set_ylabel('角度')

class all(QWidget):
    def __init__(self, parent=None):
        super(all, self).__init__(parent)
        self.initUi()

    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=5, height=4, dpi=100)
        self.mpl.start_static_plot() # 如果你想要初始化的时候就呈现静态图，请把这行注释去掉
        self.layout.addWidget(self.mpl)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = all()
    ui.mpl.start_static_plot()  # 测试静态图效果
    ui.show()
    sys.exit(app.exec_())