import sys
import json
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import webbrowser
# import math

#Cargamos el archivo .ui
gui_uic = uic.loadUiType("gui.ui")

class Interfaz(gui_uic[0], gui_uic[1]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('PokéLids Checker')
        areas = json.load(open('database/areas.json'))
        prefectures = json.load(open('database/prefectures.json'))
        self.ids = json.load(open('database/ids.json'))
        self.url_map = ""
        self.url_general_map = ""
        map = QPixmap('map.png')
        self.map.setPixmap(map)
        self.map.setScaledContents(True)
        self.area1.clicked.connect(lambda:self.load_prefectures(areas, "Area_1"))
        self.area2.clicked.connect(lambda:self.load_prefectures(areas, "Area_2"))
        self.area3.clicked.connect(lambda:self.load_prefectures(areas, "Area_3"))
        self.area4.clicked.connect(lambda:self.load_prefectures(areas, "Area_4"))
        self.area5.clicked.connect(lambda:self.load_prefectures(areas, "Area_5"))
        self.area6.clicked.connect(lambda:self.load_prefectures(areas, "Area_6"))
        self.listWidgetIds.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.comboBoxPrefectures.currentIndexChanged.connect(lambda:self.load_cities(prefectures))
        self.listWidgetCities.currentItemChanged.connect(lambda:self.load_ids(prefectures))
        self.listWidgetIds.currentItemChanged.connect(lambda:self.load_info(self.ids))
        self.gotomap.clicked.connect(lambda:self.openurl(self.url_map))
        self.gotogeneralmap.clicked.connect(lambda:self.openurl(self.url_general_map))
        self.obtained.clicked.connect(lambda:self.update_obtained(self.selected_id, self.ids))
        self.exit.clicked.connect(lambda:exit())
        self.progressBarTotal.reset()
        self.progressBarPrefecture.reset()
        self.progressBarCity.reset()
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(8)
        self.frame.setStyleSheet("color: rgb(32, 116, 48)")
        self.action_Reset_DB.triggered.connect(lambda:self.reset_db(self.ids))

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

    def reset_db(self, ids):
        for id in ids:
            ids[id]["obtained"] = "false"
        with open('database/ids.json', 'w') as archivo:
            json.dump(ids, archivo, indent=2)
            archivo.close()
        self.clear_routine()

    def update_general_progress(self, ids):
        self.totalLids = len(ids)
        self.progressBarTotal.setRange(0, self.totalLids)
        count = 0
        for lids in ids:
            if (ids[lids]["obtained"] == "true"):
                count+=1
        self.totalProgress = count
        self.progressBarTotal.setValue(self.totalProgress)
        self.progressLabelTotal.setText(str(self.totalProgress) + "/" + str(self.totalLids))

    def update_prefecture_progress(self, ids, cities_list):
        totalprefecturesids = 0
        count = 0
        for city in cities_list:
            for lids in ids:
                if (ids[lids]["city"] == city.capitalize() or ids[lids]["city"] == city.lower()):
                    totalprefecturesids+=1
                    if (ids[lids]["obtained"] == "true"):
                        count +=1
        self.prefectureLids = totalprefecturesids
        self.progressBarPrefecture.setRange(0, self.prefectureLids)
        self.prefectureProgress = count
        self.progressBarPrefecture.setValue(self.prefectureProgress)
        self.progressLabelPrefecture.setText(str(self.prefectureProgress) + "/" + str(self.prefectureLids))
    
    def update_city_progress(self, ids, ids_listed):
        self.cityLids = len(ids_listed)
        self.progressBarCity.setRange(0, self.cityLids)
        count = 0
        for lids in ids_listed:
            if (ids[lids]["obtained"] == "true"):
                count+=1
        self.cityProgress = count
        self.progressBarCity.setValue(self.cityProgress)
        self.progressLabelCity.setText(str(self.cityProgress) + "/" + str(self.cityLids))

    def load_prefectures(self, areas, name):
        self.update_general_progress(self.ids)
        self.comboBoxPrefectures.clear()
        area_prefectures = areas.get(name, {}).get("prefecture", [])
        for prefecture in area_prefectures:
            self.comboBoxPrefectures.addItem(str(prefecture))
            
    def load_cities(self, prefectures):
        prefecture = self.comboBoxPrefectures.currentText()
        self.listWidgetCities.clear()
        selected_prefecture = prefectures.get(prefecture, {}).get("lids",{})
        self.cities_list = list()
        for data in selected_prefecture:
            new_city = data.get("city", {}).capitalize()
            if new_city not in self.cities_list:
                self.cities_list.append(new_city)
        self.cities_list.sort()
        self.update_prefecture_progress(self.ids, self.cities_list)
        for city in self.cities_list:
            self.listWidgetCities.addItem(str(city))
        self.listWidgetCities.setCurrentRow(0)
    
    def load_ids(self, prefectures):
        prefecture = self.comboBoxPrefectures.currentText()
        selected_city = self.listWidgetCities.currentItem()
        if selected_city is not None:
            city = selected_city.text()
            self.listWidgetIds.clear()
            selected_prefecture = prefectures.get(prefecture, {})
            self.id_list = list()
            self.url_general_map = str(selected_prefecture["pmap"])
            for data in selected_prefecture.get("lids",{}):
                if (data["city"] == city.capitalize() or data["city"] == city.lower()):
                    self.id_list.append((data["id"]))
            self.id_list.sort()
            self.update_city_progress(self.ids, self.id_list)
            for element in self.id_list:
                self.listWidgetIds.addItem(element)
            self.listWidgetIds.setCurrentRow(0)

    def load_info(self, ids):
        selected_item = self.listWidgetIds.currentItem()
        if selected_item is not None:
            self.selected_id = selected_item.text()            
        if self.selected_id != "":
            selected_id = ids.get(self.selected_id)
            self.imageLid.setPixmap(QPixmap('images/' + str(selected_id["uid"]) + '.png'))
            self.imageLid.setScaledContents(True)
            self.listWidget.clear()
            for pkmn in selected_id["pokemon"]:
                self.listWidget.addItem(QListWidgetItem(str(pkmn).capitalize()))
            self.url_map = str(selected_id["map"])
            if (selected_id["obtained"] == "true"):
                self.obtained.setChecked(True)
            else:
                self.obtained.setChecked(False)

    def update_obtained(self, selected_id, ids):
        if self.obtained.isChecked():
            ids[selected_id]["obtained"] = "true"
        else:
            ids[selected_id]["obtained"] = "false"
        with open('database/ids.json', 'w') as archivo:
            json.dump(ids, archivo, indent=2)
            archivo.close()
        self.update_general_progress(self.ids)
        self.update_city_progress(ids, self.id_list)
        self.update_prefecture_progress(self.ids, self.cities_list)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    principal = Interfaz()
    # x = math.trunc((QCoreApplication.instance().desktop().screenGeometry().width() - principal.width()) / 2.0)
    # y = math.trunc((QCoreApplication.instance().desktop().screenGeometry().height() - principal.height()) / 2.0)
    # principal.setGeometry(x,y,principal.width(),principal.height())
    principal.show()
    sys.exit(app.exec_())