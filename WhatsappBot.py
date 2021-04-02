from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pyttsx3
import pywhatkit as whatsapp
from datetime import datetime

driver =webdriver.Chrome("C:/Program Files (x86)/chromedriver.exe")
mouth=pyttsx3.init()
def driveSite(weblink):
    driver.get(weblink)
def loginWhatsapp():
    driveSite("http://web.whatsapp.com")
    mouth.say("Kindly Scan this QR Code from your cell phone")
    mouth.runAndWait()
    driver.implicitly_wait(60)
def insert_contact(partial_name, contactnumber):
    file = open("Contacts.txt")
    file.write(partial_name+","+contactnumber+"\n")
def getList(files):
    file=open(files,'r')
    content = file
    d=dict()
    for line in content:
        cn, n=line.split(",")
        d[cn]=n
    return d
def sendMessage(message):
    contactsdict=getList("Contacts.txt")
    for i in contactsdict:
        number = contactsdict.get(i)
        print(number)
        current_hour=datetime.now().hour
        current_minute=datetime.now().minute+1
        whatsapp.sendwhatmsg(number, message,current_hour,current_minute)
def closeWeb():
    driver.close()
loginWhatsapp()
sendMessage("Hello this is automated message sent by Aadarsh Mehdi")
closeWeb()
