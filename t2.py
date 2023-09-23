import sys
from src.gologin import GoLogin
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QHeaderView, QSizePolicy,QPlainTextEdit, QTabWidget, QComboBox, QCheckBox,QStyle, QStyleOptionButton, QMessageBox, QDialog, QRadioButton,QFormLayout
from PyQt5.QtCore import QSize, Qt, QObject, pyqtSignal, pyqtSlot, QThread, QTimer, QRect
from PyQt5.QtGui import QFont, QIcon
import subprocess
import requests
import importlib
import asyncio
from worker_manager import WorkerManager
import datetime
from utils import UtilsClass
import time
# import json
# from form_gologin_offline import show_function2

class FlatUI(QWidget):
    def __init__(self):
        super().__init__()
        self.utils = UtilsClass()
        self.worker = WorkerManager()
        self.init_ui()
        self.apply_styles()
        self.threads = {}
        
        self.worker.iMess.connect(self.task_completed)
        self.go = GoLogin({
                 "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                 "profile_id": "64e8a90e201e7a42c049ccb9",
                })
        # print("Before show_function2: ", hasattr(self, "utils"))
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Tạo QTabWidget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab cho Function 1
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Gologin Online")
        self.show_function1()

        # Tab cho Function 2 (Bạn có thể thêm vào sau này)
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "Gologin Offline")
        # Tại đây, bạn có thể gọi một hàm tương tự show_function1 để tạo nội dung cho tab này
        self.show_function2()
        
        # Log Footer
        log_label = QLabel("Logs:")
        main_layout.addWidget(log_label)
        
        self.log_display = QPlainTextEdit(self)
        self.log_display.setReadOnly(True)  # Đặt ở chế độ chỉ đọc
        self.log_display.setFont(QFont('Arial', 10))
        self.log_display.setFixedHeight(int(0.3 * self.height()))
        main_layout.addWidget(self.log_display)
        # Thiết lập chiều rộng cho log_label
        
        self.setWindowTitle("By Linux")
        self.resize(1060, 860)

    def show_function1(self):
        layout = QVBoxLayout(self.tab1)

        # QHBoxLayout cho hai ô
        hbox = QHBoxLayout()

        # Layout cho ô thứ nhất
        box1_layout = QVBoxLayout()
        
        # QPlainTextEdit cho ô thứ nhất
        self.text_area1 = QPlainTextEdit(self)
        self.text_area1.setPlaceholderText("Nhập token gologin vào đây")
        self.text_area1.setFont(QFont('Arial', 12))
        self.text_area1.setFixedHeight(100)
        box1_layout.addWidget(self.text_area1)

        # QPushButton cho ô thứ nhất
        self.btn_file = QPushButton(QIcon("path_to_icon.png"), "Import")
        self.btn_file.setIconSize(QSize(24, 24))
        self.btn_file.setObjectName("purpleButton")
        self.btn_file.clicked.connect(self.on_button_click1)
        box1_layout.addWidget(self.btn_file)
        
        # Thêm layout của ô thứ nhất vào hbox
        hbox.addLayout(box1_layout)

        # Layout cho ô thứ hai
        box2_layout = QVBoxLayout()

        # QComboBox cho ô thứ hai
        # QLabel
        # platform_label = QLabel("Chọn platform:", self)
        # box2_layout.addWidget(platform_label)
        self.profile_type = QComboBox(self)
        self.profile_type.addItems(["Windows", "Mac", "Mac M1", "Linux"])
        box2_layout.addWidget(self.profile_type)
        
        # QHBoxLayout cho profile_input và nút submit
        input_hbox = QHBoxLayout()

        # QLineEdit cho ô thứ hai
        self.profile_input = QLineEdit(self)
        self.profile_input.setPlaceholderText("Nhập số lượng profile")
        input_hbox.addWidget(self.profile_input)

        # QPushButton cho ô thứ hai
        self.btn_create_profile = QPushButton("Tạo Profile")
        # Kết nối nút này với một hàm xử lý khi được nhấn, ví dụ:
        self.btn_create_profile.clicked.connect(self.create_profile_function)
        input_hbox.addWidget(self.btn_create_profile)

        # Thêm input_hbox vào box2_layout
        box2_layout.addLayout(input_hbox)
        
        # Thêm layout của ô thứ hai vào hbox
        hbox.addLayout(box2_layout)

        # Thêm hbox vào layout chính
        layout.addLayout(hbox)

        # QTableWidget
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(7)
        
        
        headers = ["","Action", "Status", "Name", "Profile ID", "Browser Type", "User Agent"]
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.resizeRowsToContents()
        
        header = CheckBoxHeader(self.table_widget,mainwindow=self)
        self.table_widget.setHorizontalHeader(header)
        header.checkBoxClicked.connect(self.check_all_rows)
        
        # QPushButton cho ô thứ nhất
        self.btn_file = QPushButton(QIcon("path_to_icon.png"), "Tải profile về")
        self.btn_file.setIconSize(QSize(24, 24))
        self.btn_file.setObjectName("downloadButton")
        self.btn_file.clicked.connect(self.on_button_download)
        box1_layout.addWidget(self.btn_file)
        
        layout.addWidget(self.table_widget)
    ###############################

    def show_function2(self):
        layout = QVBoxLayout(self.tab2)

        # QTableWidget
        self.table_widget2 = QTableWidget(self)
        self.table_widget2.setColumnCount(8)


        headers = ["","Action", "Status", "Profile Name", "Profile ID", "Proxy", "WS", "Log"]
        self.table_widget2.setHorizontalHeaderLabels(headers)
        
        self.update_table2()
            
            
        self.table_widget2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = CheckBoxHeader(self.table_widget2,mainwindow=self)
        self.table_widget2.setHorizontalHeader(header)
        header.checkBoxClicked.connect(self.check_all_rows)
            
        layout.addWidget(self.table_widget2)
        
        # Tạo QHBoxLayout cho hai nút
        button_layout = QHBoxLayout()

        # Tạo và thêm nút "load profile" vào button_layout
        load_button = QPushButton("Reload Profile", self)
        button_layout.setObjectName("purpleButton")
        button_layout.addWidget(load_button)
        load_button.clicked.connect(self.update_table2)  # Bạn cần tạo hàm load_profile_function() riêng

        # Tạo và thêm nút "xóa profile" vào button_layout
        delete_button = QPushButton("Xóa Profile", self)
        delete_button.setObjectName("downloadButton")
        button_layout.addWidget(delete_button)
        # delete_button.clicked.connect(self.delete_profile_function)  # Bạn cần tạo hàm delete_profile_function() riêng

        # Thêm button_layout vào layout chính
        layout.addLayout(button_layout)
    ###############################    
    
    def clear_body(self):
        # Hàm này sẽ xóa tất cả các widget hiện có trong body_layout
        for i in reversed(range(self.body_layout.count())): 
            widget = self.body_layout.itemAt(i).widget()
            if widget is not None: 
                widget.deleteLater()        
    def on_button_click1(self):
        print("Button clicked!")
        # Khởi động ứng dụng Node.js ngầm
        # self.input_value1 = self.text_area1.toPlainText()
        self.input_value1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTA3Zjg3ZWRkZTk5MGJhZjMzZjk0OTciLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NTA3Zjk4YTI2ZmM4M2FhMzkxNTAzNjEifQ.c3XoCI5q2gGESLoixPmVGTIDfWYRmEF-WiKBvx4reoY"
        if not self.input_value1:
            return

        url = "https://api.gologin.com/browser/v2?page=4"
        headers = {
            "Authorization": "Bearer "+self.input_value1,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        data["isToken"] = self.input_value1
        data["isProfileLink"] = ""
        data["status"] = ""
        # self.result_label.setText(f"Response: {data}")
        # print(f"Response: {data}")
        if 'profiles' in data:
            self.update_table1(data['profiles'],data["isToken"])
            self.worker.pushToProcess(data)
            
        else:
            print(f"Message: {data['message']}")

    def on_button_download(self):
        data_list = []
        for row in range(self.table_widget.rowCount()):
            container_widget = self.table_widget.cellWidget(row, 0)
            checkbox = container_widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                item = self.table_widget.item(row, 4)
                if item:
                    data_list.append(item.text())

        # Khởi tạo và chạy thread
        self.download_thread = DownloadProfileThread(self.go, self.input_value1, data_list, self.utils)
        self.download_thread.log_signal.connect(self.log)
        self.download_thread.start()

        return data_list
        
    def update_table1(self, profiles,token):
            
        self.table_widget.clearContents()
        
        self.checkbox_all = QCheckBox()
        self.checkbox_all.stateChanged.connect(self.check_all_rows)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Resize cho vừa kích thước checkbox
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Để cột "Action" vẫn được resize
        self.table_widget.setCellWidget(0, 0, self.checkbox_all)
        
        
        for row, profile in enumerate(profiles):
            self.table_widget.insertRow(row)
            # Thêm QCheckBox cho từng dòng
            checkbox_container = QWidget()
            checkbox_layout = QVBoxLayout(checkbox_container)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox = QCheckBox()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            self.table_widget.setCellWidget(row, 0, checkbox_container)
            # Tạo nút "Start" cho dòng hiện tại
            start_button = QPushButton("Download")
            start_button.setObjectName("listfunction1")
            start_button.setIcon(QIcon("path_to_icon.png"))  # Set an icon for the button
            start_button.clicked.connect(lambda checked, r=token: self.go.downloadLocalProfileZip(r,profile['id']))  # Kết nối nút "Start" với hàm start_function
            self.table_widget.setCellWidget(row, 1, start_button)  # Thêm nút "Start" vào ô cell
            
            # Thêm ô trống cho cột trạng thái
            status_item = QTableWidgetItem("")
            self.table_widget.setItem(row, 2, status_item)

            name_item = QTableWidgetItem(profile['name'])
            id_item = QTableWidgetItem(profile['id'])
            browser_type_item = QTableWidgetItem(profile['browserType'])
            browser_type_item = QTableWidgetItem(profile['browserType'])
            navigator_item = QTableWidgetItem(profile['navigator']['userAgent'])

            self.table_widget.setItem(row, 3, name_item)
            self.table_widget.setItem(row, 4, id_item)
            self.table_widget.setItem(row, 5, browser_type_item)
            self.table_widget.setItem(row, 6, navigator_item)
        
        msg = "get token from gologin"
        self.log(msg)

    def update_table2(self):
        self.table_widget.clearContents()
        profiles = self.utils.load_profile() 
        if profiles:
            self.table_widget2.clearContents()
            
            self.checkbox_all2 = QCheckBox()
            self.checkbox_all2.stateChanged.connect(self.check_all_rows2)
            self.table_widget2.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Resize cho vừa kích thước checkbox
            self.table_widget2.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Để cột "Action" vẫn được resize
            self.table_widget2.setCellWidget(0, 0, self.checkbox_all2)
            
            data={}
            data["profiles"]=[]
            for row, profile in enumerate(profiles):
                # print(profile)
                self.table_widget2.insertRow(row)
                # Thêm QCheckBox cho từng dòng
                checkbox_container = QWidget()
                checkbox_layout = QVBoxLayout(checkbox_container)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox = QCheckBox()
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                self.table_widget2.setCellWidget(row, 0, checkbox_container)
                # Tạo nút "Start" cho dòng hiện tại
                start_button = QPushButton("Start")
                start_button.setObjectName("listfunction1")
                start_button.setIcon(QIcon("path_to_icon.png"))  # Set an icon for the button
                start_button.clicked.connect(lambda checked, r=row: self.start_function_offline(r))  # Kết nối nút "Start" với hàm start_function
                self.table_widget2.setCellWidget(row, 1, start_button)  # Thêm nút "Start" vào ô cell
                
                # Thêm ô trống cho cột trạng thái
                status_item = QTableWidgetItem("")
                self.table_widget2.setItem(row, 2, status_item)

                name_item = QTableWidgetItem(profile["name"])
                self.table_widget2.setItem(row, 3, name_item)
                
                profileId = QTableWidgetItem(profile["profile_id"])
                self.table_widget2.setItem(row, 4, profileId)
                
                # Thêm ô trống cho cột proxy
                if profile.get('iproxy') is not None:
                    iproxy = profile['iproxy']
                    eproxy = "" if not iproxy.get('host') else iproxy['mode']+'://'+iproxy['host']+':'+iproxy['port']+':'+iproxy['username']+':'+iproxy['password']
                    proxy = QTableWidgetItem(str(eproxy))
                else: 
                    proxy = QTableWidgetItem("")
                self.table_widget2.setItem(row, 5, proxy)
                # Kết nối sự kiện itemChanged với hàm onItemChanged
                
                # Thêm ô trống cho cột ws
                ws = QTableWidgetItem("")
                self.table_widget2.setItem(row, 6, ws)
                
                # Thêm ô trống cho cột trạng thái
                log_item = QTableWidgetItem("")
                self.table_widget2.setItem(row, 7, log_item)
                
                dataprofile = {
                    "row":row,
                    "id":profile["profile_id"],
                    "name":profile["name"]
                }
                data["profiles"].append(dataprofile)
            # print(data)

            self.table_widget2.itemDoubleClicked.connect(self.onProxyChanged)
            self.worker.pushToProcessOffline(data)
        
    
    def onProxyChanged(self,item):
        # Kiểm tra xem item thay đổi có thuộc cột 0 không
        if item.column() == 5:
            selected_row = item.row()
            proxy = self.table_widget2.item(item.row(), 5).text()
            profile_id = self.table_widget2.item(item.row(), 4).text()
            self.showSocksDialog(selected_row,profile_id)
            
    def showSocksDialog(self,row,profile_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Proxy")  # Đặt tên cho header của dialog

        layout = QVBoxLayout()

        # Socks type
        socks_type_layout = QHBoxLayout()  # Tạo một QHBoxLayout mới cho Socks Type
        self.socks5_radio = QRadioButton("Socks5")
        self.http_radio = QRadioButton("HTTP")
        self.socks5_radio.setChecked(True)
        socks_type_layout.addWidget(QLabel("Socks Type:"))
        socks_type_layout.addWidget(self.socks5_radio)
        socks_type_layout.addWidget(self.http_radio)
        layout.addLayout(socks_type_layout)  # Thêm QHBoxLayout vào QVBoxLayout chính


        # Socks input
        self.socks_input = QLineEdit()
        layout.addWidget(QLabel("Socks:"))
        layout.addWidget(self.socks_input)
        self.socks_input.editingFinished.connect(lambda:self.parse_proxy_format(row))

        # Host and Port
        host_port_layout = QHBoxLayout()
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        host_port_layout.addWidget(QLabel("Host:"))
        host_port_layout.addWidget(self.host_input)
        host_port_layout.addWidget(QLabel("Port:"))
        host_port_layout.addWidget(self.port_input)
        layout.addLayout(host_port_layout)

        # Username and Password
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        layout.addLayout(form_layout)

        # Close button
        close_button = QPushButton("Update")
        close_button.clicked.connect(lambda:self.parse_proxy_format(row,profile_id,True))
        close_button.setObjectName("purpleButton")
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec_()
        
        
    def parse_proxy_format(self,row,profile_id = None,update=False):
        proxy_str = self.socks_input.text().strip()  
        idata = {
                "row": row,
                "id": profile_id,
                "iproxy":{
                    "mode": "",
                    "host": "",
                    "port": "",
                    "username": "",
                    "pass": ""
                }
            }
        if proxy_str:
            if self.socks5_radio.isChecked():
                socks_type = "socks5"
            elif self.http_radio.isChecked():
                socks_type = "http"
            else:
                socks_type = "Unknown"
            if "@" in proxy_str:
                # Định dạng: user:pass@ip:port
                user_pass, ip_port = proxy_str.split("@")
                user, password = user_pass.split(":")
                ip, port = ip_port.split(":")
            elif len(proxy_str.split(":")) == 4:
                # Định dạng: ip:port:user:pass
                ip, port, user, password = proxy_str.split(":")
            else:
                # Định dạng: ip:port
                ip, port = proxy_str.split(":")
                user, password = "", ""
            # linux:Ghyk123@195.154.43.184:37955	
            idata = {
                "row": row,
                "id": profile_id,
                "iproxy":{
                    "mode": socks_type,
                    "host": ip,
                    "port": port,
                    "username": user,
                    "password": password
                }
            }
            data = idata["iproxy"]
            if not update:
                self.host_input.setText(data['host'])
                self.port_input.setText(data['port'])
                if user and password:
                    self.username_input.setText(data['username'])
                    self.password_input.setText(data['password'])
        if update:    
            res = self.utils.update_proxy(idata)
            self.task_completed(res)
            if res.get('res')=='Success':
                updatesock =  "" if not idata['iproxy']['host'] else socks_type+'://'+proxy_str
                qupdate = QTableWidgetItem(str(updatesock))
                self.table_widget2.setItem(row, 5, qupdate)
                        
                    
    
    def check_all_rows(self, checked):
        for row in range(self.table_widget.rowCount()):
            chk_box = self.table_widget.cellWidget(row, 0).layout().itemAt(0).widget()
            if checked:
                chk_box.setChecked(True)
            else:
                chk_box.setChecked(False)
                
    def check_all_rows2(self, checked):
        for row in range(self.table_widget2.rowCount()):
            chk_box = self.table_widget2.cellWidget(row, 0).layout().itemAt(0).widget()
            if checked:
                chk_box.setChecked(True)
            else:
                chk_box.setChecked(False)
                
                
    def handle_selected_rows(self):
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 0)
            if checkbox.isChecked():
                # Xử lý hàng đã được chọn
                pass

            
    def start_function(self, row, token):
        # self.manager = WorkerManager()
        # Lấy nút hiện tại từ cell
        current_button = self.table_widget.cellWidget(row, 0)
        checkFunc = current_button.text()
        profile_id = self.table_widget.item(row, 3).text()
        # print(f"{checkFunc}-{profile_id}")
        # Thay đổi nhãn và kết nối của nút
        data = {
            "offline":'true',
            "row":row,
            "profileId":profile_id,
            "token":token
        }
        if checkFunc == "Start":
            # Khởi tạo và lưu trữ thread
            thread = BrowserThread(self.worker, data)
            self.threads[profile_id] = thread
            # Kết nối tín hiệu để xóa thread khi nó hoàn thành
            thread.finished.connect(lambda: self.remove_thread(profile_id))
            thread.start()
            
            current_button.setText("Stop")
            current_button.setObjectName("listfunction2")
            current_button.setStyleSheet("")
            
            
        if checkFunc == "Stop":
            current_button.setText("Start")
            # Dừng thread dựa trên profile_id và thay đổi nhãn nút
            if profile_id in self.threads:
                
                thread = self.threads[profile_id]
                # Dừng thread
                thread.stop()
                QTimer.singleShot(5000, lambda: thread.terminate()) # Dừng thread (hãy chắc chắn rằng việc này không gây ra vấn đề cho mã của bạn)
                current_button.setText("Start")
                current_button.setObjectName("listfunction1")
                current_button.setStyleSheet("")
                self.update_status(row, "Stoped")
            
    def start_function_offline(self, row):
        # self.manager = WorkerManager()
        # Lấy nút hiện tại từ cell
        current_button = self.table_widget2.cellWidget(row, 1)
        checkFunc = current_button.text()
        profile_name = self.table_widget2.item(row, 3).text()
        profile_id = self.table_widget2.item(row, 4).text()
        profile_proxy = self.table_widget2.item(row, 5).text() if self.table_widget2.item(row, 5).text() else ""
        ws = self.table_widget2.item(row, 6).text() if self.table_widget2.item(row, 5).text() else ""
        data = self.utils.looad_Preferences(profile_id)
        mergdata = {
            "offline":'true',
            "row": row,
            "ws": ws
        }
        data.update(mergdata)
        # print(f"{checkFunc}-{data}")
        # return
        # Thay đổi nhãn và kết nối của nút
        # return
        if checkFunc == "Start":
            # Khởi tạo và lưu trữ thread
            thread = BrowserThread(self.worker, data)
            self.threads[profile_id] = thread
            # Kết nối tín hiệu để xóa thread khi nó hoàn thành
            thread.finished.connect(lambda: self.remove_thread(profile_id))
            thread.start()
            self.update_status(row, "Run",2)
            
            current_button.setText("Stop")
            current_button.setObjectName("listfunction2")
            current_button.setStyleSheet("")
            
            
        if checkFunc == "Stop":
            # current_button.setText("Start")
            # Dừng thread dựa trên profile_id và thay đổi nhãn nút
            if profile_id in self.threads:
                
                thread = self.threads[profile_id]
                # Dừng thread
                thread.stop(data)
                QTimer.singleShot(5000, lambda: thread.terminate()) # Dừng thread (hãy chắc chắn rằng việc này không gây ra vấn đề cho mã của bạn)
                current_button.setText("Start")
                current_button.setObjectName("listfunction1")
                current_button.setStyleSheet("")
                self.update_status(row, "Stoped",2)


    def create_profile_function(self):
        self.input_value1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTA3Zjg3ZWRkZTk5MGJhZjMzZjk0OTciLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NTA3Zjk4YTI2ZmM4M2FhMzkxNTAzNjEifQ.c3XoCI5q2gGESLoixPmVGTIDfWYRmEF-WiKBvx4reoY"
        slprofile = int(self.profile_input.text())
        if slprofile > 0:
            self.log(f"Bắt đầu khởi tạo {slprofile} profiles")
            self.thread = CreateProfileThread(self.go, self.input_value1, int(self.profile_input.text()))
            self.thread.log_signal.connect(self.log)  # Kết nối signal từ thread tới hàm log của bạn
            self.thread.start()
        # print(res)
        # self.show_message_dialog("Thông báo","Đang code thêm!!!")
    
    def update_status(self, row, status,col=1):
        # print(col)
        status_item = QTableWidgetItem(str(status))
        self.table_widget2.setItem(row, col, status_item)

    # ... (các phần khác của mã của bạn)
    def remove_thread(self, profile_id):
        # """Xóa thread khỏi từ điển sau khi nó hoàn thành."""
        if profile_id in self.threads:
            del self.threads[profile_id]

    def handle_thread_result(self, result):
        print("Thread result:", result)
        # Cập nhật trạng thái trong bảng (nếu cần)
    
    @pyqtSlot(dict)
    def task_completed(self,result):
        # print(f"result from worker: {result.get('row')}")
        msg = (f"{result}")
        if result.get('row')!="" or result.get('row')!=None:
            self.update_status(result['row'],result['isStatus'],2)
            
        if result.get('ws')!=None:
            self.update_status(result['row'],result['ws'],6)
            
        self.log(msg)
        # res = self.worker.toJson(result)
            
            
        # print(f"result from worker: {result[row]}")
        # print(f"result from worker: {result[isStatus]}")
    
        
    def show_message_dialog(self,title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
        
    def log(self, message):
        """
        Update the log widget with a timestamp and message.
        
        Parameters:
        - log_widget: A QTextEdit or similar widget for displaying logs.
        - message: The log message to append.
        """
        current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        log_entry = f"{current_time}: {message}"
        self.log_display.appendPlainText(log_entry)
        
    def apply_styles(self):
        
        style = """QWidget {
            background-color: #FFFFFF;
        }

        QPlainTextEdit {
            border: 1px solid #E0E0E0;
            border-radius: 1px;
            padding: 10px;
        }

        QPushButton {
            background-color: #E0E0E0;
            border: none;
            padding: 5px 15px;
            border-radius: 1px;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #D0D0D0;
        }

        QPushButton:pressed {
            background-color: #C0C0C0;
        }

        QTableWidget {
            border: none;
            gridline-color: #D0D0D0;
        }

        QHeaderView::section {
            background-color: #E0E0E0;
            padding: 5px;
            border: 1px solid #D0D0D0;
        }

        QLabel {
            font-size: 14px;
            padding: 10px 0;
        }

        QLabel#footerLabel {
            font-size: 10px;  /* Cỡ chữ nhỏ*/
            color: #666666;  /* Màu chữ xám*/
            padding: 10px 0; /* Padding trên và dưới để tạo khoảng cách*/
            border-top: 1px solid #D0D0D0;
        }

        QLineEdit {
            padding: 5px 10px;
            font-size: 14px;
            border: 1px solid #D0D0D0;
            border-radius: 1px;
        }

        QPushButton#purpleButton {
            background-color: #63B8FF; /* Màu tím nhạt */
            color: black; /* Màu chữ */
        }

        QPushButton#purpleButton:hover {
            background-color: #00BFFF; /* Một tông tím sáng hơn một chút khi di chuột qua */
        }
        QPushButton#downloadButton {
            background-color: #ed5f5f; /* Màu tím nhạt */
            color: black; /* Màu chữ */
        }

        QPushButton#downloadButton:hover {
            background-color: #e63c3c; /* Một tông tím sáng hơn một chút khi di chuột qua */
        }

        QPushButton#listfunction1 {
            border: none;
            color: black;
            background-color: #00CD66;
            border-radius: 0px;
        }
        QPushButton#listfunction1:hover {
            border: none;
            background-color: #008B45;
            /* color: white; */
            border-radius: 0px;
        }
        QPushButton#listfunction2 {
            border: none;
            color: black;
            background-color: #E74C3C;
            border-radius: 0px;
        }
        QPushButton#listfunction2:hover {
            border: none;
            background-color: #C0392B;
            /* color: white; */
            border-radius: 0px;
        }
        
        QTabWidget::pane {
            border: none;
        }

        QTabBar::tab {
            background: #E0E0E0;
            border: 1px;
            padding: 7px;
            margin: 2px;
        }

        QTabBar::tab:selected {
            background: #D0D0D0;
        }

        QTabBar::tab:hover {
            background: #C0C0C0;
        }
        QComboBox {
            border: none;                     /* Loại bỏ viền */
            background-color: #f2f2f2;       /* Màu nền */
            padding: 7px;                    /* Khoảng cách padding */
            font: 12px Arial;                /* Phông chữ và kích cỡ */
            color: #555;                     /* Màu chữ */
        }

        QComboBox::drop-down {
            width: 20px;                     /* Độ rộng của nút dropdown */
            border: none;                    /* Loại bỏ viền */
            background: transparent;        /* Màu nền trong suốt */
        }

        QComboBox::down-arrow {
            image: url(path_to_arrow_icon.png);  /* Đường dẫn tới hình ảnh mũi tên. Bạn có thể thay thế bằng hình ảnh mà bạn muốn */
        }

        QComboBox QAbstractItemView {
            border: 1px solid #aaa;          /* Viền cho danh sách các mục khi mở dropdown */
            background-color: #f2f2f2;      /* Màu nền */
        }

        QComboBox::item:selected {
            background-color: #ddd;         /* Màu nền của mục được chọn */
        }        
        """

        self.setStyleSheet(style)    
        
        
class CheckBoxHeader(QHeaderView):
    checkBoxClicked = pyqtSignal(bool)

    def __init__(self, parent=None, mainwindow=None):
        super(CheckBoxHeader, self).__init__(Qt.Horizontal, parent)
        self.mainwindow = mainwindow
        self.setStretchLastSection(True)
        self.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.checkBox = QCheckBox()
        self.checkBox.setChecked(False)
        self.checkBox.stateChanged.connect(self.emitCheckBoxClicked)
        self.all_checked = False

    def emitCheckBoxClicked(self):
        self.checkBoxClicked.emit(self.checkBox.isChecked())

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()
        if logicalIndex == 0:
            # Điều chỉnh lại vị trí của checkbox để nó nằm giữa cột
            x = int(rect.x() + (rect.width() - self.checkBox.sizeHint().width()) / 2)
            y = int(rect.y() + (rect.height() - self.checkBox.sizeHint().height()) / 2)
            
            checkbox_rect = QRect(x, y, self.checkBox.sizeHint().width(), self.checkBox.sizeHint().height())
            style = QApplication.style()
            option_button = QStyleOptionButton()
            option_button.rect = checkbox_rect
            option_button.state = QStyle.State_Enabled | QStyle.State_Active
            if self.all_checked:
                option_button.state |= QStyle.State_On
            style.drawControl(QStyle.CE_CheckBox, option_button, painter)   
    
    def mousePressEvent(self, event):
        super(CheckBoxHeader, self).mousePressEvent(event)

        # Xác định vị trí của chuột
        x = event.pos().x()
        y = event.pos().y()

        # Xác định QRect cho checkbox dựa trên vị trí
        checkbox_rect = QRect(
            int((self.sectionSize(0) - self.checkBox.sizeHint().width()) / 2),
            int((self.sectionSize(0) - self.checkBox.sizeHint().height()) / 2),
            self.checkBox.sizeHint().width(),
            self.checkBox.sizeHint().height()
        )

        # Kiểm tra xem chuột có nhấp vào vùng của checkbox hay không
        if checkbox_rect.contains(x, y):
            # Đảo trạng thái của checkbox và cập nhật lại bảng
            self.all_checked = not self.all_checked
            if self.mainwindow:
                self.mainwindow.check_all_rows(self.all_checked)
            
class BrowserThread(QThread):
    # Signal to update the status in the table
    updateStatus = pyqtSignal(int, str)
    
    def __init__(self, manager, data):
        super().__init__()
        self.data = data
        self.manager = manager

    def run(self):
        if self.data['offline']:
            self.manager.run_browser_offline(self.data)
        else:
            self.manager.run_browser(self.row, self.profile_id)
        
    def stop(self,data):
        self.manager.stopGo(data)

class CreateProfileThread(QThread):
    # Tạo một signal để gửi thông báo từ thread này tới main thread
    log_signal = pyqtSignal(str)

    def __init__(self, go, input_value1, slprofile):
        super().__init__()
        self.go = go
        self.input_value1 = input_value1
        self.slprofile = slprofile

    def run(self):
        for index in range(self.slprofile):
            option = {
                "name": f'LVT_{index+1}',
                "os": 'mac',
                "navigator": {
                    "language": 'en-US',
                    "userAgent": 'random',
                    "resolution": '1024x768',
                    "platform": 'mac',
                },
                'proxy': {
                    'mode': 'none', # Specify 'none' if not using proxy
                    'autoProxyRegion': 'us' ,
                    "host": '',
                    "port": '',
                    "username": '',
                    "password": '',
                },
                "webRTC": {
                    "mode": "alerted",
                    "enabled": True,
                },
            }
            res = self.go.create(self.input_value1, option)
            self.log_signal.emit(f"Profile {index} đã được tạo: {res}")
            time.sleep(3)
 
class DownloadProfileThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, go, input_value1, data_list, utils):
        super().__init__()
        self.go = go
        self.input_value1 = input_value1
        self.data_list = data_list
        self.utils = utils

    def run(self):
        for profile_id in self.data_list:
            check_profile_exits = self.utils.load_profile(True)
            if profile_id in check_profile_exits:
                msg = (f"Profile:{profile_id} đã tồn tại)")
                self.log_signal.emit(msg)
            else:
                self.go.downloadLocalProfileZip(self.input_value1, profile_id)
                msg = (f"Đang tải profile:{profile_id}...")
                self.log_signal.emit(msg)
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlatUI()
    window.show()
    sys.exit(app.exec_())
