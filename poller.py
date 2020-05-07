import time
import urllib.parse
from threading import Thread, Lock
import pandas as pd
from selenium import webdriver
from fenetre import MainWindow

import tkinter as tk
class DataPoller(Thread):
    def __init__(self, name, condition=None, timer=0, refresh=10):
        Thread.__init__(self)
        self.lock = Lock()
        self.running = False

        self.game_id = 730 #id de cs go (url)
        self.item_name = name #idem
        self.condition = condition #pour arme 

        self.start_time = 0 #cb de temps le programme doit tourner
        self.timer = timer
        self.refresh = refresh #temps de rafraichissement de scraping

        # url_name = "{} ({})".format(self.item_name, self.condition)
        url_name = "{}".format(self.item_name)
        parsed_name = urllib.parse.quote(url_name) #convertir le nom en nom pour url
        self.adresse = "https://steamcommunity.com/market/listings/{game_id}/{item_name}" \
                        .format(game_id=self.game_id, item_name=parsed_name)
        
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(20)
        self.driver.get(self.adresse)

        self.buf = []


    timer_check = lambda self: time.time() - self.start_time > self.timer and self.timer > 0  #temps écouler depuis l'ouverture du programme (regard si supérieur au timer imposé)

    def run(self):
        self.running = True
        self.start_time = time.time()
        try:
            while True:
                if not self.running or self.timer_check():
                    # self.stop()
                    break
                
                with self.lock:
                    self.scrap_data()

                time.sleep(self.refresh)
            
        finally:
            self.driver.close()
            print("close driver")

    def stop(self):
        with self.lock:
            self.running = False
            print("stop ", self.item_name)

    def is_running(self):
        with self.lock:
            return self.running

    def scrap_data(self):

        # building link to locate price and quantity of  items
        sale = "market_commodity_buyrequests"
        xpath_quantity = "//div[@id='{}']/span[1]".format(sale)
        xpath_price = "//div[@id='{}']/span[2]".format(sale)

        # get element
        quantity_element = self.driver.find_element_by_xpath(xpath_quantity)
        price_element = self.driver.find_element_by_xpath(xpath_price)

        # clean element 
        time_stamp = int(time.time())
        quantity = int(quantity_element.text)
        price = float(price_element.text.replace("$", ""))

        self.buf.append([time_stamp, quantity, price])#time_stamp en seconde depuis le 1er janvier 1970

    def get_data(self): #remplir la dataframe avec le buf puis le vider
        with self.lock:
            buf = list(self.buf)
            self.buf = []
            return buf



def scrapping_start(liste_choix):
    
    poller=[]
    case_scrap=[]
    GLOBAL_COUNTER = 1
    print(liste_choix)
    
    for name in liste_choix:
        poller.append(DataPoller(name,timer = 3))
    for thread in liste_choix:
        poller[liste_choix.index(thread)].start()
    for thread in liste_choix:
        poller[liste_choix.index(thread)].join()

    for case in liste_choix:
        case_scrap.append(poller[liste_choix.index(case)].get_data_frame())
    for case in liste_choix:
        case_scrap[liste_choix.index(case)].to_csv("{name}.csv".format(name=liste_choix[liste_choix.index(case)]))
        return case_scrap
    """recup_case = scn.RecupCase()
    name_case = recup_case.recup()
    
    root = tk.Tk()
    app = scn.MainWindow(master=root)
    app.mainloop()
    name_choose=app.name_choose
    
    
    poller_choose =  DataPoller(name_choose, timer=1200)
    #poller_prisma = DataPoller("Prisma 2 Case", timer=1200)
    #poller_phoenix = DataPoller("Operation Phoenix Weapon Case", timer=1200)

    poller_choose.start()
    #poller_prisma.start()
    #poller_phoenix.start()


    
    poller_choose.join()
    
    df_choose=poller_choose.get_data_frame()
    #df_prisma = poller_prisma.get_data_frame()
    #df_phoenix = poller_phoenix.get_data_frame()
    
    df_choose.to_csv("{name}.csv".format(name=name_choose))
    #df_prisma.to_csv("prisma.csv")
    #df_phoenix.to_csv("phoenix.csv")"""
    