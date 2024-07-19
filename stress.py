import matplotlib.pyplot as plt
from scipy.fftpack import fft
import numpy as np
import openpyxl
import random
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改
        self.axes.cla()  # 每次绘图的时候不保留上一次绘图的结果

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # 绘制图形
    def start_static_plot(self):
        # 创建workbook
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(['时间', '数据'])
        # 生成数据
        x = []
        y = []
        for i in range(0, 60):
            nowTime = i
            randomNum = random.random() - 0.5
            x.append(nowTime)
            y.append(randomNum)
            sheet.append([str(nowTime)[0:8], str(randomNum)[0:8]])
        wb.save('应力数据.xlsx')

        self.axes.plot(x[0:60], y[0:60])
        self.axes.set_title('应力图')
        self.axes.set_ylabel('幅值')
        self.axes.set_xlabel('时间/s')

class stress(QWidget):
    def __init__(self, parent=None):
        super(stress, self).__init__(parent)
        self.initUi()

    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=5, height=4, dpi=100)
        self.mpl.start_static_plot()
        self.layout.addWidget(self.mpl)