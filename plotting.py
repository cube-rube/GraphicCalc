import matplotlib.pyplot as plt
from numpy import sin, cos, tan, log, sqrt
import numpy as np
import matplotlib as mpl


class Plot:
    def __init__(self):
       
        self.xoffset = 0
        self.yoffset = 0
        self.scale = 0

        self.xl_lim = -10
        self.xr_lim = 10
        self.yd_lim = -10
        self.yu_lim = 10

        plt.style.use('_mpl-gallery')

        self.fig = plt.figure(figsize=(5, 5), dpi=100)

        self.ax = self.fig.add_subplot()
        self.ax.spines['bottom'].set_position(('data', 0.0))
        self.ax.spines['left'].set_position(('data', 0.0))
        self.ax.spines['right'].set_color(None)
        self.ax.spines['top'].set_color(None)
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.yaxis.set_ticks_position('left')

        self.ax.set(xlim=(self.xl_lim, self.xr_lim), xticks=np.arange(self.xl_lim, self.xr_lim + 1, 1),
           ylim=(self.yd_lim, self.yu_lim), yticks=np.arange(self.yd_lim, self.yu_lim + 1, 1))
    
    def transform(self, equation:str):
        equation = equation.replace(' ', '')
        equation = equation.replace('^', '**')
        if equation.find(',') > -1 and equation.find('log(') == -1:
            raise SyntaxError
        else:
            equation = equation.replace(',', ')/log(')
        if equation.find('x') == -1:
            equation += '+(x*0)'
        equation = equation.replace('y=', '')
        return equation
    
    def plot(self, equation, color):
        if self.scale >= 0:
            self.xl_lim = -10 * (self.scale + 1) + self.xoffset * (self.scale + 1)
            self.xr_lim = 10 * (self.scale + 1) + self.xoffset * (self.scale + 1)
            self.yd_lim = -10 * (self.scale + 1) + self.yoffset * (self.scale + 1)
            self.yu_lim = 10 * (self.scale + 1) + self.yoffset * (self.scale + 1)

            self.ax.set(xlim=(self.xl_lim, self.xr_lim), xticks=np.arange(self.xl_lim, self.xr_lim + 1, 1 + self.scale),
            ylim=(self.yd_lim, self.yu_lim), yticks=np.arange(self.yd_lim, self.yu_lim + 1, 1 + self.scale))

            x = np.linspace(self.xl_lim, self.xr_lim, 25 * (self.xr_lim - self.xl_lim))
            y = eval(self.transform(equation))
        else:
            self.xl_lim = -10 / (abs(self.scale) + 1) + self.xoffset / (abs(self.scale) + 1)
            self.xr_lim = 10 / (abs(self.scale) + 1) + self.xoffset / (abs(self.scale) + 1)

            self.yd_lim = -10 / (abs(self.scale) + 1) + self.yoffset / (abs(self.scale) + 1)
            self.yu_lim = 10 / (abs(self.scale) + 1) + self.yoffset / (abs(self.scale) + 1)

            self.ax.set(xlim=(self.xl_lim, self.xr_lim), xticks=np.arange(self.xl_lim, self.xr_lim, 1 / (abs(self.scale) + 1)),
            ylim=(self.yd_lim, self.yu_lim), yticks=np.arange(self.yd_lim, self.yu_lim, 1 / (abs(self.scale) + 1)))

            x = np.linspace(self.xl_lim, self.xr_lim, 25 * int(self.xr_lim - self.xl_lim))
            y = eval(self.transform(equation))

        self.ax.plot(x, y, color=color, linewidth=1.0)
        
    def saveFile(self, filename):
        plt.savefig(filename)
