import matplotlib.pyplot as plt
import numpy as np
import scipy
import sys
import requests
import astropy.units as u
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.stats import sigma_clipped_stats
from astropy.io import fits
from astropy import table
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from photutils import DAOStarFinder
from matplotlib.colors import LogNorm
from astropy.wcs import WCS
from bs4 import BeautifulSoup
import PyQt5
from PyQt5 import uic


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('design.ui', self)

        self.error = Error()

        self.contact_link = self.findChildren(QLabel)[2]
        self.name = self.findChildren(QLineEdit)[0]

        self.save_btn = self.findChildren(QPushButton)[0]
        self.save_btn.clicked.connect(self.parsing)

        self.layout = self.findChildren(QVBoxLayout)[0]

    def parsing(self):
        galaxy_name = self.name.text()  # имя созвездия

        if len(galaxy_name) > 3:
            self.error.show()
            return 0

        home_page = f'https://dr12.sdss.org/fields/name?name={galaxy_name}'

        html = requests.get(home_page).text  # получаем страницу этого созвездия
        soup = BeautifulSoup(html, 'html.parser')  # парсим данные с этой страницы

        dl = soup.find('dl', class_='dl-horizontal')  # ищем среди данных тег "DL"
        dds = [dd for dd in dl.find_all('dd')]  # в полученых данных ищем все теги 'DD'
        links = [link for link in dds[1].find_all('a')]  # среди всех "DD" ищем теги с сылками

        url_fits = 'https://dr12.sdss.org' + links[1]['href']

        r = requests.get(url_fits)  # запрашиваем файл

        with open(r'N:\python\GalaxyVisualisator\name.fits.bz2', 'wb') as file :
            file.write(r.content)

        self.plt_widget = FigureCanvasQTAgg(self.image_rendering())  # создаем виджет с картинкой

        for i in reversed(range(self.layout.count())) :  # удаляем предыдущие картинки
            self.layout.itemAt(i).widget().setParent(None)

        self.layout.addWidget(self.plt_widget)  # добавляем новую

    def image_rendering(self):
        master_fits = fits.open('name.fits.bz2')[0]
        data = master_fits.data
        print(data)
        wcs = WCS(master_fits.header)

        fig, ax = plt.subplots()
        plt.imshow(data, origin='lower', norm=LogNorm(vmax=5e3))
        plt.axis('off')
        fig.savefig('fig.jpg')
        return fig


class Error(QWidget):
    def __init__(self):
        super(Error, self).__init__()
        self.setWindowTitle('ошибка!')
        self.main_layout = QVBoxLayout(self)
        self.text = QLabel('Invalid galaxy name', self)
        self.main_layout.addWidget(self.text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
