import webbrowser

import matplotlib.pyplot as plt
import sys
import requests
import astropy.units as u
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit, QSizePolicy
from astropy.io import fits
from astropy import table
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.colors import LogNorm
from astropy.wcs import WCS
from bs4 import BeautifulSoup
import PyQt5
from PyQt5 import uic, QtGui


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('win.ui', self)  # подгружаем дизайн

        self.error = Error()

        self.contacts = self.findChildren(QPushButton)[0]
        self.contacts.clicked.connect(lambda: webbrowser.open('https://vk.com/id510788594'))

        self.name = self.findChildren(QLineEdit)[0]
        self.wait = self.findChildren(QLabel)[1]

        self.save_btn = self.findChildren(QPushButton)[1]
        self.save_btn.clicked.connect(self.parsing)


        self.img_layout = self.findChildren(QVBoxLayout)[0]
        self.lbl = QLabel(self)
        self.pix = QtGui.QPixmap('cat2.jpg')
        self.lbl.setPixmap(self.pix)
        self.img_layout.addWidget(self.lbl)


    def parsing(self):
        galaxy_name = self.name.text()  # имя созвездия

        home_page = f'https://dr12.sdss.org/fields/name?name={galaxy_name}'

        html = requests.get(home_page).text  # получаем страницу этого созвездия
        soup = BeautifulSoup(html, 'html.parser')  # парсим данные с этой страницы

        dl = soup.find('dl', class_='dl-horizontal')  # ищем среди данных тег "DL"

        if dl == None:  # Проверяем существует ли данные о запрошенной галактике
            self.error.show()  # если нет, выводим ошибку
            return 0

        dds = [dd for dd in dl.find_all('dd')]  # в полученых данных ищем все теги 'DD'
        links = [link for link in dds[1].find_all('a')]  # среди всех "DD" ищем теги с сылками

        url_fits = 'https://dr12.sdss.org' + links[1]['href']

        r = requests.get(url_fits)  # запрашиваем файл

        with open(r'N:\python\GalaxyVisualisator\name.fits.bz2', 'wb') as file :
            file.write(r.content)

        self.plt_widget = FigureCanvasQTAgg(self.image_rendering())  # создаем виджет с картинкой

        for i in reversed(range(self.img_layout.count())) :  # удаляем предыдущие картинки
            self.img_layout.itemAt(i).widget().setParent(None)

        self.img_layout.addWidget(self.plt_widget)  # добавляем новую

    def image_rendering(self):
        master_fits = fits.open('name.fits.bz2')[0]
        data = master_fits.data
        wcs = WCS(master_fits.header)

        fig, ax = plt.subplots()
        plt.imshow(data, origin='lower', norm=LogNorm(vmax=5e3))
        plt.axis('off')
        fig.savefig('fig.jpg')
        return fig


class Error(QWidget):
    def __init__(self):
        super(Error, self).__init__()
        uic.loadUi('error.ui', self)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Galaxy Visualisator')
        self.setFixedSize(1341, 697)
        self.setCentralWidget(Window())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
