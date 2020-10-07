#!/usr/bin/env python
# coding: utf-8

# In[6]:


import json
import pyttsx3
import requests
import speech_recognition as sr
import re
import time
import threading

# we need from parseHub. 
API_KEY = "tDyPS28i8WzJ"        #change the your own string which you can get from parseHub
PROJECT_TOKEN = "tU2EbpG9FkFT"  #change the your own string which you can get from parseHub
RUN_TOKEN = "tM-fkBSfznJ_"      #change the your own string which you can get from parseHub


# class Data which contains the data of corona website https://www.worldometers.info/coronavirus/ and also the update of data from the website 
class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data',params={"api_key": API_KEY})
        data =json.loads(response.text)
        return data
    
    
    def info_Total_Cases(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['selection1']

            
    def info_Total_Deaths(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Deaths:":
                return content['selection1']

        return "0"
    
    
    def get_country_data(self,country):
        data =self.data["Country"]

        for content in data:
            if content['name'].lower() == country.lower():
                return content

        return "0"
    
    def get_list_of_countries(self):
        countries = []
        for country in self.data['Country']:
            countries.append(country['name'].lower())

        return countries
    
    def update_data(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run',params=self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data updated")
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()

# using pyttsx3 library (text to speech) when we get the data in string and present it in speech 
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# using speech_recognition library in order to recognize our speech .
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()

# main function containing our speech pattern and then by calling specific function get the result.   
def main():
    print("Strated Program")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop"
    country_list = data.get_list_of_countries()

    TOTAL_PATTERNS = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.info_Total_Cases,
        re.compile("[\w\s]+ total cases"): data.info_Total_Cases,
        re.compile("[\w\s]+ total [\w\s] + deaths"): data.info_Total_Deaths,
        re.compile("[\w\s]+ total deaths"): data.info_Total_Deaths
    }
    
    
    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['New_Cases']

    }
    
    UPDATE_COMMAND = "update"
    while True:
        print("Listening....")
        text = get_audio()
        print(text)
        result = None
        
        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break
        
        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break
        
        
        if text == UPDATE_COMMAND:
            result = "Data is being updated. This may take a moment"
            speak("Data is being updated. This may take a moment")
            data.update_data()
            
        if result:
            speak(result)
                   
        if text.find(END_PHRASE) != -1: 
            speak("OK AMIN SEE YOU")
            print("Exit")
            break

main()




