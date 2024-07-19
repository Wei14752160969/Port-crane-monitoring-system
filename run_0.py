from PyQt5 import QtWidgets, QtCore
from login import Ui_Dialog
from main import Ui_MainWindow as form_ok
from error import Ui_Form as form_no
import numpy as np
import pandas as pd
import xlrd
from scipy.fftpack import fft
from PyQt5.QtWidgets import *

import serial
import serial.tools.list_ports
import openpyxl
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QMainWindow, QGridLayout
from PyQt5.QtCore import QTimer, pyqtSlot, QThread
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from nidaqmx.constants import AcquisitionType, TaskMode
import nidaqmx
import pprint

# smtplib 用于邮件的发信动作
import smtplib
from email.mime.text import MIMEText
# email 用于构建邮件内容
from email.header import Header
from email.mime.text import MIMEText  # 专门发送正文
from email.mime.multipart import MIMEMultipart  # 发送多个部分
from email.mime.application import MIMEApplication  # 发送附件


class mywindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.btn_ok.clicked.connect(self.printState)

    def printState(self):
        # 显示状态
        if self.lineEdit_username.text().strip() == "yzu" and self.lineEdit_password.text() == "123456":
            words = "Login successful!"
            self.w1 = window_ok()
            self.w1.show()
            self.hide()
        else:
            words = "Login faild!"
            self.w2 = window_no()
            self.w2.show()
            self.hide()
        self.label_state.setText(words)

class Myplot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        # normalized for 中文显示和负号
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # new figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # activate figure window
        # super(Plot_dynamic,self).__init__(self.fig)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        # self.fig.canvas.mpl_connect('button_press_event', self)
        # sub plot by self.axes
        self.axes = self.fig.add_subplot(111)
        # initial figure
        self.compute_initial_figure()

        # size policy
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class time_fig(Myplot):
    def __init__(self, *args, **kwargs):
        Myplot.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        counts = [1, 10]
        delay_t = [0, 1]
        self.axes.plot(delay_t, counts, '-ob')
        self.axes.set_xlabel("时间(s)")
        self.axes.set_ylabel("幅值")

class frequency_fig(Myplot):
    def __init__(self, *args, **kwargs):
        Myplot.__init__(self, *args, **kwargs)
    def compute_initial_figure(self):
        y = [1, 10]
        x = [0, 1]
        self.axes.plot(x, y, '-ob')
        self.axes.set_xlabel("时间(s)")
        self.axes.set_ylabel("v-v(m/s)")

class window_ok(QtWidgets.QMainWindow, form_ok):
    def __init__(self):
        super(window_ok, self).__init__()
        self.setupUi(self)
        self.setvalue1()
        self.setvalue2()
        self.setvalue3()
        self.setvalue4()
        self.setvalue5()
        self.setvalue6()
        self.setvalue7()
        self.setvalue8()
        self.setvalue_stress()
        self.setvalue_angle()
        self.domain1_btn.clicked.connect(self.domain1)
        self.domain2_btn.clicked.connect(self.domain2)
        self.domain3_btn.clicked.connect(self.domain3)
        self.domain4_btn.clicked.connect(self.domain4)
        self.domain5_btn.clicked.connect(self.domain5)
        self.domain6_btn.clicked.connect(self.domain6)
        self.domain7_btn.clicked.connect(self.domain7)
        self.domain8_btn.clicked.connect(self.domain8)
        self.stress_btn.clicked.connect(self.stress)
        self.angle1_btn.clicked.connect(self.angle1)
        self.save_btn.clicked.connect(self.save)
        self.share_btn.clicked.connect(self.share)

        self.init()
        self.ser = serial.Serial()
        self.port_check()
        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))

        self.fig1 = time_fig(width=5, height=3, dpi=72)
        self.fig2 = frequency_fig(width=5, height=3, dpi=72)
        self.gridlayout1 = QGridLayout(self.Plot_time)
        self.gridlayout2 = QGridLayout(self.Plot_frequency)
        self.gridlayout1.addWidget(self.fig1)
        self.gridlayout2.addWidget(self.fig2)
        # initialized flags for static/dynamic plot: on is 1,off is 0
        self._timer = QTimer(self)
        self._t = 0
        self._counts = []
        self._delay_t = []
        self.save_t = []
        self.save_counts = []
        self._Static_on = 0
        self._update_on = 0

    global nc
    nc = 1

    @pyqtSlot()
    def on_dynamic_plot_clicked(self):
        print('start dynamic ploting')
        self.dynamic_plot.setEnabled(False)
        # start update figure every 1s; flag "update_on" : 1 is on and 0 is Off
        self._update_on = 1
        self._timer.timeout.connect(self.update_fig)
        self._timer.start(1000)  # plot after 1s delay



    def update_fig(self):
        self._t += 1
        print(self._t)
        self._delay_t.append(self._t)
        self.save_t.append(self._t)
        print(self._delay_t)
        # new_counts=random.randint(100,900)
        pp = pprint.PrettyPrinter(indent=4)
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("cDAQ1Mod2/ai2")
            task.timing.cfg_samp_clk_timing(25600, sample_mode=AcquisitionType.CONTINUOUS)
            data = task.read(number_of_samples_per_channel=1)
            pp.pprint(data)
        new_counts = data[0]
        self._counts.append(new_counts)
        self.save_counts.append(new_counts)
        if new_counts >= 100:
            self.share()
        print(self._counts)
        self.fig1.axes.cla()
        if len(self._delay_t) > 120:
            del(self._delay_t[0])
            del(self._counts[0])
        self.fig1.axes.plot(self._delay_t, self._counts)
        self.fig1.axes.set_xlabel("时间(s)")
        self.fig1.axes.set_ylabel("幅值")
        self.fig1.draw()

        # yy = fft(self._counts)  # 快速傅里叶变换
        # yreal = yy.real  # 获取实数部分
        # yimag = yy.imag  # 获取虚数部分

        yf = abs(fft(self._counts))  # 取绝对值
        # yf1 = abs(fft(self._counts)) / len(self._delay_t)  # 归一化处理
        # yf2 = yf1[range(int(len(self._delay_t) / 2))]  # 由于对称性，只取一半区间

        # xf = np.arange(len(self._counts))  # 频率
        # xf1 = xf
        # xf2 = xf[range(int(len(self._delay_t) / 2))]  # 取一半区间
        self.fig2.axes.cla()
        self.fig2.axes.plot(self._delay_t, yf, 'r')
        self.fig2.axes.set_xlabel("时间(s)")
        self.fig2.axes.set_ylabel("v-v(m/s)")
        self.fig2.draw()

        _translate = QtCore.QCoreApplication.translate
        result = self.save_counts
        df_mean = np.mean(result)
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        df_var = np.var(result)
        df_std = np.std(result)
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        df_max = np.amax(result)
        df_min = np.amin(result)
        df_pp = df_max - df_min
        df_a = np.mean(x ** 3)
        df_b = np.mean(x ** 4)
        df_S = df_rms / df_mean_abs
        df_C = df_max / df_rms
        df_I = df_max / df_mean_abs
        df_CL = df_max / df_r
        df_K = df_b / df_rms ** 4
        self.value_mean.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value_mean_abs.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value_variance.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value_std.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value_rms.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value_sra.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value_max.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value_min.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value_vv.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value_skew.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value_kurtosis.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value_w.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value_v.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value_p.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value_m.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value_k.setText(_translate("MainWindow", str(df_K)[0:8]))

    def save(self):
        # 创建workbook
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(['时间', '数据'])
        for i in range(0, len(self.save_t)):
            nowTime = self.save_t[i]
            nowdata = self.save_counts[i]
            sheet.append([str(nowTime), str(nowdata)[0:8]])
        wb.save('数据1.xlsx')

    def share(self):
        # 发信方的信息：发信邮箱，QQ 邮箱授权码
        from_addr = '971120584@qq.com'
        password = 'jhzavidxrirtbebi'

        # 收信方邮箱
        to_addr = '971120584@qq.com'

        # 发信服务器
        smtp_server = 'smtp.qq.com'
        # 邮件头信息
        msg = MIMEMultipart()
        msg['From'] = Header(from_addr)
        msg['To'] = Header(",".join(to_addr))
        msg['Subject'] = Header('监测系统警报')

        # 构建正文
        part_text = MIMEText('请查收数据文件')
        msg.attach(part_text)  # 把正文加到邮件体里面去

        # 构建邮件附件

        file = '数据1.xlsx'  # 附件路径
        part_attach1 = MIMEApplication(open(file, 'rb').read())  # 打开附件
        part_attach1.add_header('Content-Disposition', 'attachment', filename=file)  # 为附件命名
        msg.attach(part_attach1)  # 添加附件

        # 开启发信服务，这里使用的是加密传输
        server = smtplib.SMTP_SSL(smtp_server)
        server.connect(smtp_server, 465)
        # 登录发信邮箱
        server.login(from_addr, password)
        # 发送邮件
        server.sendmail(from_addr, to_addr, msg.as_string())
        # 关闭服务器
        server.quit()

    @pyqtSlot()
    def on_End_plot_clicked(self):
        if self._update_on == 1:
            self._update_on = 0
            self._timer.timeout.disconnect(self.update_fig)
            self.dynamic_plot.setEnabled(True)
        else:
            pass

    @pyqtSlot()
    def on_Erase_plot_clicked(self):
        self.fig1.axes.cla()
        self._counts = []
        self._delay_t = []
        self.save_t = []
        self.save_counts = []
        self.fig1.draw()
        self.fig2.axes.cla()
        self.yf = []
        self.fig2.draw()
        if self._update_on == 1:
            self._update_on = 0
            self._delay_t = []
            self._counts = []
            self.fig1.axes.cla()
            self.fig1.draw()
            self.fig2.axes.cla()
            self.fig2.draw()
            self._timer.timeout.disconnect(self.update_fig)
            self.dynamic_plot.setEnabled(True)
        else:
            pass
        # self.Erase_plot.setEnabled(False)



    def setvalue1(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据1.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value1_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value1_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value1_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value1_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value1_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value1_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value1_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value1_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value1_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value1_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value1_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value1_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value1_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value1_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value1_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value1_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue2(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据2.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value2_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value2_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value2_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value2_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value2_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value2_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value2_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value2_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value2_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value2_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value2_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value2_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value2_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value2_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value2_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value2_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue3(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据3.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value3_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value3_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value3_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value3_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value3_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value3_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value3_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value3_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value3_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value3_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value3_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value3_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value3_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value3_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value3_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value3_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue4(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据4.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value4_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value4_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value4_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value4_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value4_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value4_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value4_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value4_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value4_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value4_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value4_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value4_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value4_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value4_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value4_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value4_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue5(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据5.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value5_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value5_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value5_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value5_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value5_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value5_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value5_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value5_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value5_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value5_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value5_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value5_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value5_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value5_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value5_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value5_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue6(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据6.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value6_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value6_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value6_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value6_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value6_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value6_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value6_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value6_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value6_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value6_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value6_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value6_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value6_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value6_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value6_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value6_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue7(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据7.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value7_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value7_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value7_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value7_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value7_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value7_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value7_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value7_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value7_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value7_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value7_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value7_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value7_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value7_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value7_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value7_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue8(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("数据8.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        # 绝对平均值
        result_abs = np.abs(result)
        df_mean_abs = np.mean(result_abs)
        # 方差
        df_var = np.var(result)
        # 标准差
        df_std = np.std(result)
        # 均方根
        x = np.array(result)
        df_rms = np.sqrt(np.mean(x ** 2))
        # 方根幅值
        y = np.array(result_abs)
        r = np.mean(np.sqrt(y))
        df_r = r ** 2
        # 最大值
        df_max = np.amax(result)
        # 最小值
        df_min = np.amin(result)
        # 峰峰值
        df_pp = df_max - df_min
        # 偏斜度
        df_a = np.mean(x ** 3)
        # 峭度
        df_b = np.mean(x ** 4)
        # 波形指标
        df_S = df_rms / df_mean_abs
        # 峰值指标
        df_C = df_max / df_rms
        # 脉冲指标
        df_I = df_max / df_mean_abs
        # 裕度指标
        df_CL = df_max / df_r
        # 峭度指标
        df_K = df_b / df_rms ** 4
        self.value8_1.setText(_translate("MainWindow", str(df_mean)[0:8]))
        self.value8_2.setText(_translate("MainWindow", str(df_mean_abs)[0:8]))
        self.value8_3.setText(_translate("MainWindow", str(df_var)[0:8]))
        self.value8_4.setText(_translate("MainWindow", str(df_std)[0:8]))
        self.value8_5.setText(_translate("MainWindow", str(df_rms)[0:8]))
        self.value8_6.setText(_translate("MainWindow", str(df_r)[0:8]))
        self.value8_7.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.value8_8.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.value8_9.setText(_translate("MainWindow", str(df_pp)[0:8]))
        self.value8_10.setText(_translate("MainWindow", str(df_a)[0:8]))
        self.value8_11.setText(_translate("MainWindow", str(df_b)[0:8]))
        self.value8_12.setText(_translate("MainWindow", str(df_S)[0:8]))
        self.value8_13.setText(_translate("MainWindow", str(df_C)[0:8]))
        self.value8_14.setText(_translate("MainWindow", str(df_I)[0:8]))
        self.value8_15.setText(_translate("MainWindow", str(df_CL)[0:8]))
        self.value8_16.setText(_translate("MainWindow", str(df_K)[0:8]))
    def setvalue_stress(self):
        _translate = QtCore.QCoreApplication.translate
        data = pd.read_excel("应力数据.xlsx", usecols=['数据'])
        lie = data.values.tolist()
        result = []
        for i in lie:
            result.append(i[0])
        # 均值
        df_mean = np.mean(result)
        self.value_stress.setText(_translate("MainWindow", str(df_mean)[0:8]))
    def setvalue_angle(self):
        _translate = QtCore.QCoreApplication.translate
        angle = []
        data1 = pd.read_excel("倾角1.xlsx", usecols=['数据'])
        angle1 = data1.values.tolist()
        for i in angle1:
            angle.append(i[0])

        data2 = pd.read_excel("倾角2.xlsx", usecols=['数据'])
        angle2 = data2.values.tolist()
        for i in angle2:
            angle.append(i[0])

        data3 = pd.read_excel("倾角3.xlsx", usecols=['数据'])
        angle3 = data3.values.tolist()
        for i in angle3:
            angle.append(i[0])

        data4 = pd.read_excel("倾角4.xlsx", usecols=['数据'])
        angle4 = data4.values.tolist()
        for i in angle4:
            angle.append(i[0])

        data5 = pd.read_excel("倾角5.xlsx", usecols=['数据'])
        angle5 = data5.values.tolist()
        for i in angle5:
            angle.append(i[0])

        data6 = pd.read_excel("倾角6.xlsx", usecols=['数据'])
        angle6 = data6.values.tolist()
        for i in angle6:
            angle.append(i[0])

        data7 = pd.read_excel("倾角7.xlsx", usecols=['数据'])
        angle7 = data7.values.tolist()
        for i in angle7:
            angle.append(i[0])

        data8 = pd.read_excel("倾角8.xlsx", usecols=['数据'])
        angle8 = data8.values.tolist()
        for i in angle8:
            angle.append(i[0])

        data9 = pd.read_excel("倾角9.xlsx", usecols=['数据'])
        angle9 = data9.values.tolist()
        for i in angle9:
            angle.append(i[0])

        data10 = pd.read_excel("倾角10.xlsx", usecols=['数据'])
        angle10 = data10.values.tolist()
        for i in angle10:
            angle.append(i[0])

        data11 = pd.read_excel("倾角11.xlsx", usecols=['数据'])
        angle11 = data11.values.tolist()
        for i in angle11:
            angle.append(i[0])

        data12 = pd.read_excel("倾角12.xlsx", usecols=['数据'])
        angle12 = data12.values.tolist()
        for i in angle12:
            angle.append(i[0])

        df_max = np.amax(angle)
        df_min = np.amin(angle)
        df_current = angle[719]
        self.angle_max.setText(_translate("MainWindow", str(df_max)[0:8]))
        self.angle_min.setText(_translate("MainWindow", str(df_min)[0:8]))
        self.angle_current.setText(_translate("MainWindow", str(df_current)[0:8]))

    def domain1(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据1.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def domain2(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据2.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def domain3(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据3.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def domain4(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据4.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def domain5(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据5.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def domain6(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据6.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def domain7(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据7.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def domain8(self):
        # 打开文件
        workbook = xlrd.open_workbook('数据8.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def stress(self):
        # 打开文件
        workbook = xlrd.open_workbook('应力数据.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def angle1(self):
        # 打开文件
        workbook = xlrd.open_workbook('倾角1.xlsx')
        # 获取所有sheet
        # sheet2_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        cols = sheet1.col_values(1)  # 获取第二列内容
        # 获取整行和整列的值（数组）
        for i in range(len(cols)):
            rowslist = sheet1.row_values(i)  # 获取excel每行内容
            for j in range(len(rowslist)):
                # 在tablewidget中添加行
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                # 把数据写入tablewidget中
                newItem = QTableWidgetItem(rowslist[j])
                self.tableWidget.setItem(i - 1, j, newItem)

    def init(self):
        # 串口检测按钮
        self.s1__box_1.clicked.connect(self.port_check)

        # 串口信息显示
        self.s1__box_2.currentTextChanged.connect(self.port_imf)

        # 打开串口按钮
        self.open_button.clicked.connect(self.port_open)

        # 关闭串口按钮
        self.close_button.clicked.connect(self.port_close)

        # 发送数据按钮
        self.s3__send_button.clicked.connect(self.data_send)

        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.timer_send_cb.stateChanged.connect(self.data_send_timer)

        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

        # 清除发送窗口
        self.s3__clear_button.clicked.connect(self.send_data_clear)

        # 清除接收窗口
        self.s2__clear_button.clicked.connect(self.receive_data_clear)


    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 无串口")

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    # 打开串口
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = int(self.s1__box_3.currentText())
        self.ser.bytesize = int(self.s1__box_4.currentText())
        self.ser.stopbits = int(self.s1__box_6.currentText())
        self.ser.parity = self.s1__box_5.currentText()

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.timer.start(2)

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.formGroupBox1.setTitle("串口状态（已开启）")

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.lineEdit_3.setEnabled(True)
        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.formGroupBox1.setTitle("串口状态（已关闭）")

    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.s3__send_text.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.hex_send.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    input_s = (input_s + '\r\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_sended += num
                self.lineEdit_2.setText(str(self.data_num_sended))
        else:
            pass

    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num)
            num = len(data)
            # hex显示
            if self.hex_receive.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                self.s2__receive_text.insertPlainText(out_s)
            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.s2__receive_text.insertPlainText(data.decode('iso-8859-1'))


            # 统计接收字符的数量
            self.data_num_received += num
            self.lineEdit.setText(str(self.data_num_received))

            # 获取到text光标
            textCursor = self.s2__receive_text.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.s2__receive_text.setTextCursor(textCursor)
        else:
            pass

    # 定时发送数据
    def data_send_timer(self):
        if self.timer_send_cb.isChecked():
            self.timer_send.start(int(self.lineEdit_3.text()))
            self.lineEdit_3.setEnabled(False)
        else:
            self.timer_send.stop()
            self.lineEdit_3.setEnabled(True)

    # 清除显示
    def send_data_clear(self):
        self.s3__send_text.setText("")

    def receive_data_clear(self):
        self.s2__receive_text.setText("")



class window_no(QtWidgets.QWidget, form_no):
    def __init__(self):
        super(window_no, self).__init__()
        self.setupUi(self)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = mywindow()
    ui.show()
    sys.exit(app.exec_())
