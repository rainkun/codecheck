import os
import json
import tempfile
from PyQt5.QtCore import QObject, pyqtSignal
from src.gologin import GoLogin

class UtilsClass(QObject):
    iMess = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.path_to_profile = os.path.join(tempfile.gettempdir(), 'gologinoffline')
        self.go = GoLogin({'token':'fake'})
        
    def load_profile(self,check=False):
        
        path_to_profile = os.path.join(tempfile.gettempdir(), 'gologinoffline')
        # path_to_profile = os.path.join(pathoffline, self.profile_id)  # Thay đổi đường dẫn này tới thư mục 'profile' của bạn
        if not os.path.exists(path_to_profile):
            os.makedirs(path_to_profile)
            
        folders = [d for d in os.listdir(path_to_profile) if os.path.isdir(os.path.join(path_to_profile, d))]
        if check:
            return folders
            
        full_data = []
        if folders:
            for index,folder in enumerate(folders):
                # Mở tệp và đọc dữ liệu
                path_json = os.path.join(path_to_profile,folder,'Default', 'Preferences')
                # print(path_json)
                if not os.path.exists(path_json):
                    continue
                    
                with open(path_json, "r", encoding='utf-8') as file:
                    if not file:
                        continue
                    data = json.load(file)
                    # print(data['id'])
                    full_data.append(data['gologin'])
        return full_data
        
    def looad_Preferences(self,profile_id):
        path_to_profile = os.path.join(tempfile.gettempdir(), 'gologinoffline',profile_id)
        path_json = os.path.join(path_to_profile,'Default', 'Preferences')
        # Đọc file JSON
        with open(path_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if data.get('gologin'):
            return data['gologin']
            
    def update_proxy(self,updata):
        # print(f"{updata}")
        if updata.get('id'):
            profile_id = updata['id']
            path_to_profile = os.path.join(tempfile.gettempdir(), 'gologinoffline',profile_id)
            path_json = os.path.join(path_to_profile,'Default', 'Preferences')
            if not os.path.exists(path_json):
                res = {'row':updata['row'],'id':profile_id,'msg':'Path update not fond'}
                return res
            else:
                # Đọc file JSON
                with open(path_json, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                # Kiểm tra xem 'iproxy' có tồn tại trong 'gologin' hay không
                if data.get('gologin'):
                    if 'iproxy' not in data['gologin']:
                        data['gologin']['iproxy'] = {}  # Tạo mục 'iproxy' nếu nó chưa tồn tại
                    data['gologin']['iproxy']=updata['iproxy']
                    
                # Lưu lại dữ liệu đã cập nhật
                with open(path_json, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)
                res = {'row':updata['row'],'id':profile_id,'res':'Success','isStatus':'Proxy updated','proxy':updata['iproxy']}
                # print(data['gologin']['geolocation'])
                # return
                self.go.updateTimezone(path_json,updata['iproxy'])
                return res
        # return
        