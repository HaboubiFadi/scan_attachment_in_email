# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 13:07:39 2023

@author: Haboubi
"""
from __future__ import print_function

import imaplib
import base64
import os
import email
import time
import json
import requests
import cloudmersive_virus_api_client
from cloudmersive_virus_api_client.rest import ApiException
from pprint import pprint
from PIL import Image
import random


#Function return last mail 

def get_last_mail(user,password):
    
    
    mail=imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user,password)
    mail.select("inbox")
    
    mail.list()
    result ,data=mail.uid('search',None,"ALL")
    
    inbox_item_list=data[0].split()
    most_recent =inbox_item_list[-1]
    result2 , email_data =mail.uid("fetch",most_recent,'(RFC822)')
    raw_email =email_data[0][1].decode("utf-8")
    email_message =email.message_from_string(raw_email)
    return email_message
# function to delete files not used
def delete_file(file):
    for i in file:
        os.remove(i)
        print("delete file:",i)
       

def decode(input_text):
    pos=input_text.find("?UTF-8?B?")
    if pos>0:
        pos=pos+len("?UTF-8?B?")
        base64_string=input_text[pos:]
        print(pos)
        base64_bytes = base64_string.encode("ascii")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("UTF-8")
        return sample_string
    else:
        return input_text

# filter the attatchment file if it's an imgage type         
def filter_img(input_text):
    #input_text=input_text.lower()
    img_type=['jfif','png','bmp','jpeg','xbm','rast','tiff','ppm','pgm','pbm','gif','rgb','jpg']
    for ty in img_type:
        if ty in input_text:
            return True
    return False   
# Download the attached files    
def file_attached(email_message):
    file_name=[]
    img_name=[]
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = decode(part.get_filename())
        
        if bool(fileName):
            cwd = os.getcwd()
            file="File"
            k=os.path.join(cwd, file)
            if os.path.exists(k) == False:
                os.mkdir(k)
            
            
            
            filePath = os.path.join(k, fileName)
            if not os.path.isfile(filePath):
                fp = open(filePath, 'wb')
                
                fp.write(part.get_payload(decode=True))
                if filter_img(filePath)==True:
                    img_name.append(filePath)
                file_name.append(filePath)
                fp.close()
                
                
            subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
            print('Downloaded "{file}" from email titled "{subject}" .'.format(file=fileName, subject=subject))
    return file_name,img_name   
# use the Api to scan the files    
def scan_files(liste):
    statue=[]

    # Configure API key authorization: Apikey
    configuration = cloudmersive_virus_api_client.Configuration()
    #Add your cloudmersive_virus_api_client Key: https://api.cloudmersive.com/docs/virus.asp  
    key=""
    configuration.api_key['Apikey'] = key
    api_instance = cloudmersive_virus_api_client.ScanApi(cloudmersive_virus_api_client.ApiClient(configuration))
    # file | Input file to perform the operation on.
    try:
        # Scan a file for viruses
        for input_file in liste:
            api_response1 = api_instance.scan_file(input_file)
            #pprint(type(api_response1))
            statue.append(api_response1)

            #statue.append(api_response["found_viruses"])
            
    except ApiException as e:
        print("Exception when calling ScanApi->scan_file: %s\n" % e)
    
    
    sts=[]
    for i in statue:
        sts.append(i._found_viruses)
    #### delete files from the server
    delete_file(liste)
    return sts
# Using Eden Api to scan for explicit content    
def explict_content_det_api1(img):
    key=""

    headers={"Authorization":"Bearer "+key}
    path=converte_img(img)
    #file=img_to_bufferreader(img)
    files = {'file': open(path,'rb')}

    url="https://api.edenai.run/v2/image/explicit_content"
    data={"providers":"amazon"}
    response = requests.post(url, data=data, files=files, headers=headers)

    result = json.loads(response.text)
    return result
# convert any img type to png to avoid any complication
def converte_img(path):
    a=random.randint(0,100)
    cwd = os.getcwd()
    fileName="File"
    file_path=os.path.join(cwd, fileName)
    file_path=os.path.join(file_path,"new")
    path_to=file_path+str(a)+'.png'
    im1 = Image.open(path)
    im1.save(path_to)
    im1.close()
    return path_to
    
# test the img degree of explicity    
def test_imgs(liste):
    explicit_img=[]
    for i in liste[1]:
        statue=explict_content_det_api1(liste[1][0])
        if statue["amazon"]["nsfw_likelihood"]>3:
            explicit_img.append(statue)
    return explicit_img   
import os, re, os.path
# delete All files after we are done
def delete_all_file():
    cwd = os.getcwd()
    fileName="File"
    file_path=os.path.join(cwd, fileName)
    for root, dirs, files in os.walk(file_path):
        for file in files:
            os.remove(os.path.join(root, file))



        