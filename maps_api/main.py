from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QAction
)

import sys
import io
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent, QPixmap
from yandex_map.yandex_map import (
    get_map,
    del_map,
    get_coordinates,
    get_adres,
    get_place,
    search_business
)
from PyQt5.QtCore import Qt
from math import cos, radians


# TODO:
# 1. Большая задача по Maps API. Часть №1
# 2. Большая задача по Maps API. Часть №2
# 3. Большая задача по Maps API. Часть №3
# 4. Большая задача по Maps API. Часть №4
# 5. Большая задача по Maps API. Часть №5
# 6. Большая задача по Maps API. Часть №6
# 7. Большая задача по Maps API. Часть №7
# 8. Большая задача по Maps API. Часть №8
# 9. Большая задача по Maps API. Часть №9
# 10. Большая задача по Maps API. Часть №10
# 11. Большая задача по Maps API. Часть №11


template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>603</width>
    <height>605</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Карты</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QLabel" name="map">
    <property name="geometry">
     <rect>
      <x>0</x>
      <y>110</y>
      <width>600</width>
      <height>450</height>
     </rect>
    </property>
    <property name="text">
     <string/>
    </property>
   </widget>
   <widget class="QPushButton" name="search_button">
    <property name="geometry">
     <rect>
      <x>430</x>
      <y>10</y>
      <width>161</width>
      <height>21</height>
     </rect>
    </property>
    <property name="text">
     <string>Искать</string>
    </property>
   </widget>
   <widget class="QLineEdit" name="search_line">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>10</y>
      <width>411</width>
      <height>21</height>
     </rect>
    </property>
   </widget>
   <widget class="QLabel" name="adres">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>70</y>
      <width>571</width>
      <height>20</height>
     </rect>
    </property>
    <property name="text">
     <string/>
    </property>
   </widget>
   <widget class="QCheckBox" name="mail">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>40</y>
      <width>121</width>
      <height>21</height>
     </rect>
    </property>
    <property name="text">
     <string>Почтовый Индекс</string>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>603</width>
     <height>21</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
"""


zoom = {
    21: (25, 17),
    20: (50, 31),
    19: (100, 62),
    18: (200, 125),
    17: (400, 250),
    16: (800, 500),
    15: (1600, 1000),
    14: (3200, 2000),
    13: (6400, 4000),
    12: (12800, 8000),
    11: (25600, 16000),
    10: (51200, 32000),
    9: (102400, 64000),
    8: (204800, 128000),
    7: (409600, 256000)
}


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)
        self.initUI()
        self.settings()
        self.set_map(self.z)
    
    def settings(self):
        """
        Метод установки настроек приложения
        """
        self.xx, self.yy = 31.276086, 58.521104
        self.spn_x = 0.005
        self.spn_y = 0.008
        self.z = 15
        self.map_type = "map"
        self.file = ""
        self.pt = ""
    
    def initUI(self):
        """
        Метод интерфейса приложения
        """
        self.menu = self.menuBar()

        self.btn_map = QAction("Схема", self)
        self.btn_map.triggered.connect(lambda x: self.set_type_map("map"))

        self.btn_sat = QAction("Спутник", self)
        self.btn_sat.triggered.connect(lambda x: self.set_type_map("sat"))

        self.btn_road = QAction("Пробки", self)
        self.btn_road.triggered.connect(lambda x: self.set_type_map("trf"))

        self.map_menu = self.menu.addMenu("Карта")
        self.map_menu.addAction(self.btn_map)
        self.map_menu.addAction(self.btn_sat)
        self.map_menu.addAction(self.btn_road)

        self.map_menu.addSeparator()

        self.btn_search = QAction("Поиск", self)
        self.btn_search.triggered.connect(self.can_search)

        self.btn_clear_pt = QAction("Сброс поиска", self)
        self.btn_clear_pt.triggered.connect(self.clear_pt)

        self.map_menu.addAction(self.btn_search)
        self.map_menu.addAction(self.btn_clear_pt)

        self.search_line.setEnabled(False)
        self.search_button.setEnabled(False)
        self.mail.setEnabled(False)

        self.search_button.clicked.connect(self.search_place)
    
    def make_point(self, x: float, y: float):
        """
        Метод устанавливвающий на карту метку
        """
        self.pt = f"{str(x)},{str(y)},pm2blm"
        self.set_map(self.z)

    def clear_pt(self):
        """
        Метод очищающий карту от меток
        """
        self.pt = ""
        self.z = 15
        self.set_map(self.z)
        self.adres.setText("")

    def search_place(self):
        """
        Метод поиска места на карте по названию
        """
        if self.search_line.text():
            try:
                request = self.search_line.text()
                self.search_line.setEnabled(False)
                self.search_line.clear()
                self.xx, self.yy = get_coordinates(request)
                self.spn_x = 0.005
                self.spn_y = 0.008
                self.z = 15
                self.pt = f"{str(self.xx)},{str(self.yy)},pm2blm"
                self.set_map(self.z)
                self.search_button.setEnabled(False)
                adres = get_adres((self.xx, self.yy))
                text = "Адрес: " + adres[0]
                if self.mail.isChecked():
                    text += f", {adres[1]}"
                self.adres.setText(text)
                self.mail.setEnabled(False)
            except Exception as e:
                pass

    def can_search(self):
        """
        Метод активирующий возможность поиска
        """
        self.search_line.setEnabled(True)
        self.search_button.setEnabled(True)
        self.mail.setEnabled(True)

    def set_type_map(self, type):
        """
        Метод установки типа карты
        """
        self.map_type = type
        self.z = 15
        self.spn_x = 0.005
        self.spn_y = 0.008
        self.set_map(self.z)

    def set_map(self, z: int=False):
        """
        Метод установления карты в приложении
        """
        new_map = get_map((self.xx, self.yy), z=z, map_format=self.map_type, pt=self.pt)
        self.map.setPixmap(QPixmap(new_map))
        self.file = new_map
        if self.file:
            del_map(self.file)
        
    def check_click_on_map(self, x: int, y: int):
        """
        Метод проверки было ли нажатие по карте
        """
        return 0 <= x <= 600 and 110 <= y <= 560

    def convert_click(self, x: int, y: int):
        """
        Метод преобразует клик по экрану в координату физической карты.
        """
        # Нахожу количество градусов в пикселе
        koef_x = ((zoom[self.z][0]) / (111300)) / 600
        koef_y = ((zoom[self.z][1]) / 111300) / 450
        # koef_x = ((20 * (2 ** (21 - self.z + 1))) / (111300)) / 600
        # koef_y = ((10 * (2 ** (21 - self.z + 1))) / 111300) / 450
        # Нахожу верхнюю левую координату загруженной карты
        x0 = self.xx - koef_x * 300
        y0 = self.yy + koef_y * 225
        # Нахожу координаты клика на физической карте
        coords = (x0 + koef_x * x, y0 - koef_y * y)
        return coords
    
    def search_touch(self, x: int, y: int):
        coords = self.convert_click(x, y)
        self.make_point(*coords)
        try:
            self.adres.setText(get_place(coords))
        except Exception:
            pass
    
    def search_business(self, x: int, y: int):
        coords = self.convert_click(x, y)
        c = get_adres(coords)[0]
        self.make_point(*coords)
        data = search_business(text=c, count=1, info=True, spn=[0.0005, 0.0005])
        self.adres.setText(data["features"][0]["properties"]["name"])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            if self.check_click_on_map(x, y) and self.z >= 7:
                # Ищем объект на карте
                self.search_touch(x, y - 110)
        else:
            x, y = event.x(), event.y()
            if self.check_click_on_map(x, y) and self.z >= 7:
                self.search_business(x, y - 110)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            # Уменьшаем масштаб карты
            if self.z < 21:
                self.z += 1
                self.spn_x, self.spn_y = self.spn_x / 2, self.spn_y / 2
                self.set_map(self.z)
        elif event.key() == Qt.Key_PageDown:
            # Увеличиваем масштаб карты
            if self.z > 1:
                self.z -= 1
                self.spn_x, self.spn_y = self.spn_x * 2, self.spn_y * 2
                self.set_map(self.z)
        elif event.key() == Qt.Key_Up:
            # Движение карты вверх
            self.yy += (self.spn_y / 2)
            self.set_map(self.z)
        elif event.key() == Qt.Key_Down:
            # Движение карты вниз
            self.yy -= (self.spn_y / 2)
            self.set_map(self.z)
        elif event.key() == Qt.Key_Left:
            # Движение карты влево
            self.xx -= (self.spn_x / 2)
            self.set_map(self.z)
        elif event.key() == Qt.Key_Right:
            # Движение карты вправо
            self.xx += (self.spn_x / 2)
            self.set_map(self.z)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    map = Map()
    map.show()
    sys.exit(app.exec())