import sys
import json
import sqlite3
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import webbrowser
import math

#Cargamos el archivo .ui
gui_uic = uic.loadUiType("gui.ui")
conn = sqlite3.connect('pokemon.db')

class Interfaz(gui_uic[0], gui_uic[1]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('PokéLids Checker')
        self.area_selected = 0
        self.prefecture_selected = 0
        self.city_selected = 0
        self.lid_selected = 0
        self.url_lid_map = ""
        self.url_prefecture_map = ""
        self.totalLids = (conn.execute("SELECT COUNT(*) FROM Lids")).fetchone()[0]
        print(self.totalLids)
        map = QPixmap('map.png')
        self.map.setPixmap(map)
        self.map.setScaledContents(True)
        self.area1.clicked.connect(lambda:self.load_prefectures("1"))
        self.area2.clicked.connect(lambda:self.load_prefectures("2"))
        self.area3.clicked.connect(lambda:self.load_prefectures("3"))
        self.area4.clicked.connect(lambda:self.load_prefectures("4"))
        self.area5.clicked.connect(lambda:self.load_prefectures("5"))
        self.area6.clicked.connect(lambda:self.load_prefectures("6"))
        self.listWidgetIds.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.comboBoxPrefectures.currentIndexChanged.connect(lambda:self.load_cities())
        self.listWidgetCities.currentItemChanged.connect(lambda:self.load_ids())
        self.listWidgetIds.currentItemChanged.connect(lambda:self.load_info())
        self.gotomap.clicked.connect(lambda:self.openurl(self.url_lid_map))
        self.gotoprefecturemap.clicked.connect(lambda:self.openurl(self.url_prefecture_map))
        self.obtained.clicked.connect(lambda:self.update_obtained())
        self.exit.clicked.connect(lambda:exit())
        self.progressBarTotal.reset()
        self.progressBarPrefecture.reset()
        self.progressBarCity.reset()
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(8)
        self.frame.setStyleSheet("color: rgb(32, 116, 48)")
        self.action_Reset_DB.triggered.connect(lambda:self.reset_db())

    def openurl(self, url):
        if (url != ""):
            webbrowser.open(url)

    def clear_routine(self):
        self.comboBoxPrefectures.clear()
        self.listWidgetCities.clear()
        self.listWidgetIds.clear()
        self.listWidget.clear()
        self.obtained.setChecked(False)
        self.imageLid.clear()
        self.progressBarTotal.setValue(0)
        self.progressBarPrefecture.setValue(0)
        self.progressBarCity.setValue(0)
        self.progressLabelTotal.setText("")
        self.progressLabelPrefecture.setText("")
        self.progressLabelCity.setText("")

    def reset_db(self):
        conn.execute("UPDATE Lids SET is_registered = 0")
        conn.commit()
        self.clear_routine()

    def update_general_progress(self):
        self.progressBarTotal.setRange(0, self.totalLids)
        self.totalProgress = (conn.execute("SELECT COUNT(*) FROM Lids WHERE is_registered = 1")).fetchone()[0]
        self.progressBarTotal.setValue(self.totalProgress)
        self.progressLabelTotal.setText(str(self.totalProgress) + "/" + str(self.totalLids))

    def update_prefecture_progress(self):
        self.prefectureLids = (conn.execute("SELECT COUNT(*) FROM Lids WHERE prefecture_id = ?", (self.prefecture_selected,))).fetchone()[0]
        self.progressBarPrefecture.setRange(0, self.prefectureLids)
        self.prefectureProgress = (conn.execute("SELECT COUNT(*) FROM Lids WHERE prefecture_id = ? and is_registered = 1", (self.prefecture_selected,))).fetchone()[0]
        self.progressBarPrefecture.setValue(self.prefectureProgress)
        self.progressLabelPrefecture.setText(str(self.prefectureProgress) + "/" + str(self.prefectureLids))
    
    def update_city_progress(self):
        self.cityLids = (conn.execute("SELECT COUNT(*) FROM Lids WHERE city_id = ?", (self.city_selected,))).fetchone()[0]
        self.progressBarCity.setRange(0, self.cityLids)
        self.cityProgress = (conn.execute("SELECT COUNT(*) FROM Lids WHERE city_id = ? and is_registered = 1", (self.city_selected,))).fetchone()[0]
        self.progressBarCity.setValue(self.cityProgress)
        self.progressLabelCity.setText(str(self.cityProgress) + "/" + str(self.cityLids))

    def load_prefectures(self, area):
        self.update_general_progress()
        self.comboBoxPrefectures.clear()
        self.area_selected = area
        prefectures_by_area = conn.execute("SELECT prefecture_name FROM Prefectures WHERE area_id = ?", (self.area_selected,))
        for prefecture in prefectures_by_area.fetchall():
            self.comboBoxPrefectures.addItem(str(prefecture[0]))
            
    def load_cities(self):
        prefecture = self.comboBoxPrefectures.currentText()
        if prefecture != "":
            self.listWidgetCities.clear()
            prefecture_id = conn.execute("SELECT prefecture_id FROM Prefectures WHERE prefecture_name = ?", (prefecture,))
            self.prefecture_selected = str((prefecture_id.fetchone())[0])
            cities_by_prefecture = conn.execute("SELECT city_id FROM Lids WHERE prefecture_id = ?", (self.prefecture_selected,))
            cities_id_list = list()
            self.cities_list = list()
            for data in cities_by_prefecture.fetchall():
                new_city = (data[0])
                if new_city not in cities_id_list:
                    cities_id_list.append(new_city)
            for city_id in cities_id_list:
                city_name = conn.execute("SELECT city_name FROM Cities WHERE city_id = ?", (city_id,))
                city_name = str((city_name.fetchone())[0])
                self.cities_list.append(city_name)
            self.cities_list.sort()
            for city in self.cities_list:
                self.listWidgetCities.addItem(str(city))
            self.listWidgetCities.setCurrentRow(0)
            self.update_prefecture_progress()
    
    def load_ids(self):
        selected_city = self.listWidgetCities.currentItem()
        if selected_city is not None:
            city = selected_city.text()
            self.listWidgetIds.clear()
            self.id_list = list()
            city_selected = conn.execute("SELECT city_id FROM Cities WHERE city_name = ?", (city,))
            self.city_selected = str(city_selected.fetchone()[0])
            prefecture_map = conn.execute("SELECT prefecture_map FROM Prefectures WHERE prefecture_id = ?", (self.prefecture_selected,))
            for map in prefecture_map.fetchone():
                self.url_prefecture_map = str(map)
            lids_by_city = conn.execute("SELECT lid_id FROM Lids WHERE prefecture_id = ? AND city_id = ?", (self.prefecture_selected, self.city_selected))
            for data in lids_by_city.fetchall():
                self.id_list.append(str(data[0]))
            self.id_list.sort()
            self.update_city_progress()
            for element in self.id_list:
                self.listWidgetIds.addItem(element)
            self.listWidgetIds.setCurrentRow(0)

    def load_info(self):
        selected_item = self.listWidgetIds.currentItem()
        if selected_item is not None:
            self.lid_selected = selected_item.text()            
        if self.lid_selected != "":
            lid_selected = conn.execute("SELECT unique_id, lid_map, pokemon_list FROM Lids WHERE lid_id = ?", (self.lid_selected,))
            lid_selected = lid_selected.fetchone()
            self.imageLid.setPixmap(QPixmap('images/' + str(lid_selected[0]) + '.png'))
            self.imageLid.setScaledContents(True)
            self.listWidget.clear()
            self.url_lid_map = str(lid_selected[1])
            pkmn_list = [pkmn for pkmn in str(lid_selected[2]).split(",")]
            for pkmn in pkmn_list:
                self.listWidget.addItem(QListWidgetItem(str(pkmn).capitalize()))
            is_registered = conn.execute("SELECT is_registered FROM Lids WHERE lid_id = ?", (self.lid_selected,))
            is_registered = (is_registered.fetchone()[0])
            if (is_registered):
                self.obtained.setChecked(True)
            else:
                self.obtained.setChecked(False)

    def update_obtained(self):
        if self.obtained.isChecked():
            conn.execute("UPDATE Lids SET is_registered = 1 WHERE lid_id = ?", (self.lid_selected,))
        else:
            conn.execute("UPDATE Lids SET is_registered = 0 WHERE lid_id = ?", (self.lid_selected,))
        conn.commit()
        self.update_general_progress()
        self.update_prefecture_progress()
        self.update_city_progress()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    principal = Interfaz()
    x = math.trunc((QCoreApplication.instance().desktop().screenGeometry().width() - principal.width()) / 2.0)
    y = math.trunc((QCoreApplication.instance().desktop().screenGeometry().height() - principal.height()) / 2.0)
    principal.setGeometry(x,y,principal.width(),principal.height())
    principal.show()
    sys.exit(app.exec_())