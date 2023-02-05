import sys
import sqlite3
from datetime import datetime as dt

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem, QAbstractItemView

from ui_main import Ui_MainWindow
from ui_tablewidget import Ui_Form
from plotting import Plot

from numpy import sin, cos, tan, log, sqrt
from random import choice


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.TableWidget = None
        self.connection = sqlite3.connect("assets/history.sqlite")
        self.functionEdit.returnPressed.connect(lambda: self.enterFunc(self.functionEdit.text()))
        self.clearing.pressed.connect(self.clear)
        self.help.pressed.connect(self.openHelp)
        self.movementGroup.buttonPressed.connect(self.movement)
        self.magnifierGroup.buttonPressed.connect(self.scaling)
        self.saveAsPng.triggered.connect(self.savePng)
        self.saveInTable.triggered.connect(self.saveSql)
        self.saveInTable.setEnabled(False)
        self.openFromTable.triggered.connect(self.openWindow)
        self.openAbout.triggered.connect(self.about)
        self.helpAct.triggered.connect(self.openHelp)
        self.functions = []
        self.plot = Plot()
        self.generate('assets/data.png')
        self.loadImage()

    def about(self):
        aboutDlg = QMessageBox(self)
        aboutDlg.setWindowTitle('О программе')
        aboutDlg.setText("Графический калькулятор")
        aboutDlg.setInformativeText(
            '''GraphicalCalc
v1.0
© Sergey Telpov 2023

Версия Python - 3.10.9
Библиотеки:
PyQT5 - 5.15.7
matplotlib - 3.6.2
numpy - 1.24.1
            '''
        )
        aboutDlg.setIcon(QMessageBox.Icon.Information)
        aboutDlg.exec()
    
    def openHelp(self):
        helpDlg = QMessageBox(self)
        helpDlg.setWindowTitle('Формат вводимых данных')
        helpDlg.setText("Функции:")
        helpDlg.setInformativeText('''sqrt(x) - корень квадратный от x
sin(x) - синус x
cos(x) - косинус x
tan(x) - тангенс x
log(x) - логарифм x по основанию e
log(x, n) - логарифм x по основанию n

Примеры записи функции:

cos(x) или y=cos(x)
y=sin(x+x*2)
y=x**2 или y=x^2 (возведение в степень)
y=sin(x)+cos(x)
и другие варианты...
        ''')
        helpDlg.setIcon(QMessageBox.Icon.Information)
        helpDlg.exec()


    def enterFunc(self, func):
        try:
            color = choice(['red', 'orange', 'green', 'blue', 'purple', 'brown', 'pink', 'xkcd:grey'])
            self.functions.append((func, color))
            self.generate('assets/data.png')
            color = color.replace('xkcd:', '')
            self.loadImage()
            self.functionList.appendPlainText(func + ' (' + color + ')')
            self.functionEdit.setText('')
            self.errorLabel.setText('')
            self.saveInTable.setEnabled(True)
        except SyntaxError:
            self.errorLabel.setText('Ошибка синтаксиса')
            self.functions.pop()
        except NameError:
            self.errorLabel.setText('Ошибка имен переменных или фунций')
            self.functions.pop()
    
    def clear(self):
        self.functions = []
        self.functionList.setPlainText('')
        self.plot = Plot()
        self.generate('assets/data.png')
        self.loadImage()
        self.saveInTable.setEnabled(False)

    
    def generate(self, filename):
        for i in range(len(self.functions)):
            self.plot.plot(self.functions[i][0], self.functions[i][1])
        self.plot.saveFile(filename)
    
    def loadImage(self):
        self.plotPixmap = QPixmap('assets/data.png')
        self.plotImage.setPixmap(self.plotPixmap)
    
    def movement(self, button):
        if button.text() == '↓':
            self.plot.yoffset -= 1
        if button.text() == '↑':
            self.plot.yoffset += 1
        if button.text() == '←':
            self.plot.xoffset -= 1
        if button.text() == '→':
            self.plot.xoffset += 1
        self.generate('assets/data.png')
        self.loadImage()
    
    def scaling(self, button):
        if button.text() == 'Приблизить':
            self.plot.scale -= 1
        if button.text() == 'Отдалить':
            self.plot.scale += 1
        self.generate('assets/data.png')
        self.loadImage()
    
    def savePng(self):
        fname = QFileDialog.getSaveFileName(self,
                                            self.tr('Выбрать папку'), 
                                            'graph.png',
                                            self.tr("Image Files (*.png *.jpeg *.jpg *.webp)"))
        if fname[0]:
            if fname[0][fname[0].rfind('.'):] in ('.png', '.jpg', '.jpeg', '.webp'):
                self.generate(fname[0])
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Ошибка!")
                dlg.setText("Не удалось сохранить файл в указанном формате.")
                dlg.setIcon(QMessageBox.Icon.Critical)
                dlg.exec()
    
    def saveSql(self):
        cur = self.connection.cursor()
        itemDate = dt.now().strftime("%d/%m/%Y %H:%M:%S")
        if len(self.functions):
            cur.execute(
                f'''
                INSERT INTO items(date,graph_count) VALUES("{itemDate}",{len(self.functions)})
                '''
            )
            self.connection.commit()
            for i in range(len(self.functions)):
                cur.execute(
                    f'''
                    INSERT INTO graphs(itemId,graph) VALUES((SELECT id FROM items WHERE date = "{itemDate}"), "{self.functions[i][0]}")
                    '''
                )
            self.connection.commit()
    
    def openWindow(self):
        self.tableWidget = TableWindow(self.connection)
        self.tableWidget.show()

    def closeWindow(self, res):
        self.tableWidget.close()
        self.clear()
        for val in res:
            self.enterFunc(val[0])
        self.generate('assets/data.png')
        self.loadImage()

    def closeEvent(self, event):
        saveDlg = QMessageBox(self)
        saveDlg.setText("Вы хотите сохранить график как изображение?")
        saveDlg.setIcon(QMessageBox.Question)
        saveDlg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        saveDlg.button(QMessageBox.Save).setText('Сохранить')
        saveDlg.button(QMessageBox.Discard).setText('Не сохранять')
        saveDlg.button(QMessageBox.Cancel).setText('Отмена')
        saveDlg.setDefaultButton(QMessageBox.Save)
        saveDlg.setEscapeButton(QMessageBox.Cancel)
        if len(self.functions):
            btn = saveDlg.exec()
            if btn == QMessageBox.Save:
                self.savePng()
                if self.TableWidget:
                    self.tableWidget.close()
                    self.tableWidget = None
                event.accept()
            elif btn == QMessageBox.Discard:
                if self.TableWidget:
                    self.tableWidget.close()
                    self.tableWidget = None
                event.accept()
            elif btn == QMessageBox.Cancel: 
                event.ignore()
        else:
            if self.TableWidget:
                    self.tableWidget.close()
                    self.tableWidget = None
            event.accept()


class TableWindow(QWidget, Ui_Form):
    def __init__(self, connection:sqlite3.Connection):
        super().__init__()
        self.setupUi(self)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setToolTip("При двойном нажатии на номер серии расчетов вызывается вся серия, при двойном нажатии на функцию вызывается только эта функция")
        self.connection = connection
        cur = self.connection.cursor()
        res = cur.execute(
            '''
            SELECT
                items.id,
                items.date,
                graphs.graph
            FROM
                graphs
            LEFT JOIN items ON graphs.itemId = items.id
            '''
        ).fetchall()
        cur.close()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(len(res))
        self.fillTable(res)
        self.tableWidget.setHorizontalHeaderLabels(['Номер серии\nрасчетов', 'Дата', 'Функция'])
        self.tableWidget.cellDoubleClicked.connect(self.getFunc)
        self.searchLine.textEdited.connect(self.search)
    
    def fillTable(self, res):
        self.tableWidget.setRowCount(len(res))
        for i, elem in enumerate(res):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def search(self):
        cur = self.connection.cursor()
        res = cur.execute(
            f'''
            SELECT
                items.id,
                items.date,
                graphs.graph
            FROM
                graphs
            LEFT JOIN items ON graphs.itemId = items.id
            WHERE items.id LIKE "%{self.searchLine.text()}%" OR items.date LIKE "%{self.searchLine.text()}%" OR graphs.graph LIKE "%{self.searchLine.text()}%"
            '''
            ).fetchall()
        self.fillTable(res)

    def getFunc(self, row, col):
        cur = self.connection.cursor()
        if col == 0 or col == 1:
            res = cur.execute(
                f'''
                SELECT
                    graphs.graph
                FROM
                    graphs
                LEFT JOIN items ON graphs.itemId = items.id
                WHERE items.id = {self.tableWidget.item(row, 0).text()}
                '''
            ).fetchall()
        elif col == 2:
            res = cur.execute(
                f'''
                SELECT DISTINCT
                    graphs.graph
                FROM
                    graphs
                LEFT JOIN items ON graphs.itemId = items.id
                WHERE graphs.graph = "{self.tableWidget.item(row, 2).text()}"
                '''
            ).fetchall()
        cur.close()
        ex.closeWindow(res)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
