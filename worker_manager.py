import multiprocessing
from multiprocessing import Process, Manager

from PyQt5.QtCore import QObject, pyqtSignal,QThread
from src.autopygo import WorkerThread
import json
from src.gologin import GoLogin
import pyppeteer
import asyncio
import requests
from anticaptchaofficial.recaptchav2proxyless import *

class WorkerManager(QObject):

    iMess = pyqtSignal(dict)
    def __init__(self):
        super().__init__()  # Gọi phương thức khởi tạo của QObject
        self.processes = []
        self.threads = {}
        self.linkLocal = "http://localhost:36912/browser/start-profile"
        self.go = GoLogin({"token":"fake"})
    # def pushToProcess(self,info):
        # if isJson(info)
            
    def pushToProcess(self, info):
        # print(info)
        # self.iMess.emit(info)
        self.processes = []
        data = json.dumps(info)
        if self.isJson(data):
            json_data = json.loads(data)
            token = json_data.get("isToken")
            profiles = json_data.get("profiles")
            # print(token)
            if token and profiles:
                for item in profiles:
                    item['browser'] = None
                    item['token'] = token
                    item['isStatus'] = ""
                    item['isProfileLink'] = ""
                    item['worker_id'] = {}
                    
                self.processes = profiles
                # print(self.processes)
                # self.iMess.emit(self.processes)
        else:
            print("cccccc")
            
    def pushToProcessOffline(self, info):
        # print(info)
        # self.iMess.emit(info)
        self.processes = []
        data = json.dumps(info)
        # print(info)
        if self.isJson(data):
            json_data = json.loads(data)
            profiles = json_data.get("profiles")
            # print(profiles)
            if profiles:
                for item in profiles:
                    item['browser'] = None
                    item['isStatus'] = ""
                    item['isProfileLink'] = ""
                    item['worker_id'] = {}
                    
                self.processes = profiles
                # print(self.processes)
                # self.iMess.emit(self.processes)
        else:
            print("cccccc")
            
    def run_browser(self,data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.startGo(data))
        finally:
            loop.close()
        # asyncio.get_event_loop().run_until_complete(self.startGo(row,profileId))
    def run_browser_offline(self,data):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.startGo_offline(data))
        finally:
            loop.close()
        # asyncio.get_event_loop().run_until_complete(self.startGo(row,profileId))
        
    def stop_browser(self,row, profileId):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.stopGo(row, profileId))
        finally:
            loop.close()
        # asyncio.get_event_loop().run_until_complete(self.startGo(row,profileId))
        
    def toJson(self,i):
        data = json.dumps(i)
        return json.loads(data)
    
    async def startGo_offline(self,data):
        try:
            thisProcess = next(item for item in self.processes if item['id'] == data['profile_id'])
            # if not thisProcess:
                # proc = {
                    # "id":profileId,
                    # "row":row
                # }
                # self.processes.append(proc)
                # thisProcess = proc
            
            # indexProcess = next(item for item in enumerate(self.processes) if item['id'] == profileId)
            # thisProcess['isProfileLink']='ws://127.0.0.1:29651/devtools/browser/dd34b263-e5ee-45f5-86d1-df9c768ec6b2'
            # data = self.toJson(thisProcess)
            # print("Đã tìm thấy mảng:", thisProcess)
            # gl = GoLogin({
                # "token": thisProcess['token'],
                # "profile_id": thisProcess['id'],
            # })
            # debugger_address = gl.start()
            if not thisProcess['isProfileLink']:
                conn = await self.runBrowser_offline(data)
                browser = await pyppeteer.connect(browserWSEndpoint=conn, defaultViewport=None)
                thisProcess['isProfileLink']=conn
                # self.processes[indexProcess] = json.dump(thisProcess)
                # print(conn)
            else:
                try: 
                    browser = await pyppeteer.connect(browserWSEndpoint=thisProcess['isProfileLink'], defaultViewport=None)
                except Exception as e:
                    # print(f"Error connect: {e}")
                    conn = await self.runBrowser(data['profile_id'])
                    browser = await pyppeteer.connect(browserWSEndpoint=conn, defaultViewport=None)
                    thisProcess['isProfileLink']=conn
                    # self.processes[indexProcess] = json.dump(thisProcess)
            
            thisProcess['row']=data['row']
            thisProcess['isStatus']='running...'
            thisProcess['browser'] = browser
            res = {'row':thisProcess['row'],'isStatus':thisProcess['isStatus'],'ws':thisProcess['isProfileLink']}
            self.iMess.emit(res)
            
            worker = WorkerThread()
            await worker.runAtuo(browser,data['row'],data['profile_id'])
            # print(f"process: {thisProcess}")
            # self.start_worker(thisProcess['isProfileLink'])
            # browser.on('disconnected',self.stop_profile({'isStatus':'','row':row}));
            
        except StopIteration:
            print(f"Không tìm thấy mảng có id:", profileId)
            
            
    async def startGo(self,data):
        try:
            thisProcess = next(item for item in self.processes if item['id'] == data['profileId'])
            # thisProcess['isProfileLink']='ws://127.0.0.1:29651/devtools/browser/dd34b263-e5ee-45f5-86d1-df9c768ec6b2'
            # data = self.toJson(thisProcess)
            # print("Đã tìm thấy mảng:", thisProcess)
            # gl = GoLogin({
                # "token": thisProcess['token'],
                # "profile_id": thisProcess['id'],
            # })
            # debugger_address = gl.start()
            if not thisProcess['isProfileLink']:
                conn = await self.runBrowser(profileId)
                browser = await pyppeteer.connect(browserWSEndpoint=conn, defaultViewport=None)
                thisProcess['isProfileLink']=conn
            else:
                try: 
                    browser = await pyppeteer.connect(browserWSEndpoint=thisProcess['isProfileLink'], defaultViewport=None)
                except Exception as e:
                    print(f"Error connect: {e}")
                    conn = await self.runBrowser(profileId)
                    browser = await pyppeteer.connect(browserWSEndpoint=conn, defaultViewport=None)
                    thisProcess['isProfileLink']=conn
            
            thisProcess['row']=row
            thisProcess['isStatus']='running...'
            thisProcess['browser'] = browser
            res = {'row':thisProcess['row'],'isStatus':thisProcess['isStatus']}
            self.iMess.emit(res)
            
            worker = WorkerThread()
            await worker.runAtuo(browser,row,profileId)
            # print(f"process: {thisProcess}")
            # self.start_worker(thisProcess['isProfileLink'])
            # browser.on('disconnected',self.stop_profile({'isStatus':'','row':row}));
            
        except StopIteration:
            print(f"Không tìm thấy mảng có id:", profileId)
        
    async def checkLoginAnti(self):
        apiKey = "375b655fc65a159d59f2a9fbf558671d"
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(apiKey)
        print("account balance: " + str(solver.get_balance()))
        if str(solver.get_balance()):
            return True
        
    async def runBrowser(self,profileId):
        if not await self.checkLoginAnti():
            return
        url = self.linkLocal
        headers = {
            "Content-Type": "application/json"
        }
        postData = {
            "profileId": profileId,
            "sync": "true"
        }
        try:
            response = requests.post(url, headers=headers,json=postData)
            print(f"response: {response}")
            data = response.json()
            print(f"{data}")
            if data['status']=='success':
                return data['wsUrl']
            else:
                return False
        except Exception as b:
            print(f"Connection error, retrying...{b}")

    async def runBrowser_offline(self,data):
        if not await self.checkLoginAnti():
            return
        return self.go.start(data)
        
    async def stopGo(self,data):
        try:
            thisProcess = next(item for item in self.processes if item['id'] == data.get('profile_id'))
            browser = thisProcess['browser']
            res = {'row':data['row'],'isStatus':'Closing browser...'}
            self.iMess.emit(res)
            await browser.close()
            
        except StopIteration:
            print("Không tìm thấy mảng có id:", data.get('profile_id'))
    
    def isJson(self,data):
        # print(data)
        if not isinstance(data, (str, bytes, bytearray)):
            return False
        try:
            json.loads(data)
            return True
        except ValueError:
            return False
        
    def start_worker(self, linkProfile):
        # thisProcess = next(item for item in self.processes if item['id'] == id)
        worker = WorkerThread()
        process = multiprocessing.Process(target=worker.runAtuo, args=(linkProfile))
        process.start()
        self.threads[id] = process
    
    def stop_profile(self,e):
        self.iMess.emit(e)
    
    def stop_processes(self,profileId):
        thisProcess = next(item for item in self.processes if item['id'] == profileId)
        if thisProcess.worker_id in self.processes:
            process = self.processes[worker_id]
            process.terminate()  # Kết thúc tiến trình
            process.join()  # Đợi cho tiến trình hoàn tất  
            thisProcess['isStatus']=''
            self.iMess.emit(self.thisProcess)
