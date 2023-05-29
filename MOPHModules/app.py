import face_recognition
import cv2
import requests
import random
import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import json


# this part for encrytion

from cryptography.fernet import Fernet
import pickle
from Crypto.Cipher import AES
import pickle
import base64
from base64 import b64encode, b64decode







# ciphertext=bytes(ciphertext,'utf-8')


def decrypt(encrypted_string):
    key=b'abcdefghjkloiupu'
    iv = b'qwertyuioplkjhgf'


    aes = AES.new(key, AES.MODE_EAX, iv)
    str_tmp = b64decode(encrypted_string.encode('utf-8'))
    print("tmp",str_tmp)
    str_dec = aes.decrypt(str_tmp)
    print("dec",str_dec)
    return str_dec

# NUM=3
# def decrypt(encrypted_string):
#     new_chars=[]
#     for ch in encrypted_string:
#         x = chr(ord(ch) - NUM)
#         new_chars.append(x)

#     new_chars="".join(char for char in new_chars)
#     return new_chars
#     # return fernet._encrypt_from_parts(unencrypted_string.encode(), 0,b'\xbd\xc0,\x16\x87\xd7G\xb5\xe5\xcc\xdb\xf9\x07\xaf\xa0\xfa')


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app)

with open(r"key.pickle", "rb") as input_file:
    key=pickle.load(input_file)
print(key)
fernet = Fernet(key)



def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='moph',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM health_status;')
    persons = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', persons=persons)



@app.route('/getCovidStatusByQID/', methods=('GET', 'POST'))
@cross_origin()
def getCovidStatusByQID():
    if request.method == 'POST':
        data = request.json
        print(data.get('QID'))
        QID=str(data.get('QID'))
        

        if len(QID)!=0:
            conn = get_db_connection()
            cur = conn.cursor()
            select_qid_query="SELECT * FROM health_status where qatarid like '"+QID+"'"
            cur.execute(select_qid_query)        
            persons = cur.fetchall()
            response={}
            if len(persons)==1:
                # get his/her health status
                covid_status=persons[0][0]
                response["covid_status"]=covid_status
            else:
                response["covid_status"]="Unknown"
            response_j=jsonify(response)
            return response_j



@app.route('/update/', methods=('GET', 'POST'))
@cross_origin()
def update():
    if request.method == 'POST':        
        QID = str(request.form['qid'])                
        covid_status = request.form['covid_status']


        # we should check if the qatar id is valid
        # check using the MOI_IP
        # check using the MOI_PORT
        MOI_IP=os.environ['MOI_IP']
        MOI_PORT=os.environ['MOI_PORT']


        url = f"http://{MOI_IP}:{MOI_PORT}/searchbyQID"

        payload = json.dumps({
          "QID": QID
        })
        headers = {
          'Content-Type': 'application/json'
        }
        print("Sending request to ",url)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        data = json.loads(response.text)
        # print(response.data)
        # data = response.json
        print(data)
        # if response.is_json:
        #     data = response.json

        # else:
        #     print("Not correct response")
        #     return "Not correct response"

        if data["exists"]=="False":
            return "QID does not exist"

        # we can update/insert table now
        conn = get_db_connection()
        cur = conn.cursor()
        insert_sql = """INSERT INTO health_status(QatarID,covid_status)
        VALUES(%s,%s)
        on CONFLICT (QatarID) do
        update set covid_status=%s;"""
        cur.execute(insert_sql, (QID,covid_status,covid_status))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('update.html')

import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "moph.sdp@gmail.com"  # Enter your address
password = "jhoowshofredtdlz"



@app.route('/getemails/', methods=('GET', 'POST'))
@cross_origin()
def getemails():
    if request.method == 'POST':        
        QID = str(request.form['qid'])                
        print("Looking for QID in Mall",QID)


        # we should check if the qatar id is valid
        # check using the MOI_IP
        # check using the MOI_PORT
        MOI_IP=os.environ['MOI_IP']
        MOI_PORT=os.environ['MOI_PORT']
        MALL_IP=os.environ['MALL_IP']
        MALL_PORT=os.environ['MALL_PORT']


        url = f"http://{MALL_IP}:{MALL_PORT}/contacts"

        payload = json.dumps({
          "QID": QID
        })
        headers = {
          'Content-Type': 'application/json'
        }
        print("Sending request to mall to get contact qids",url)
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(response.text)
        data = json.loads(response.text)
        qids=data
        qids.append(QID)

        # print(response.data)
        # data = response.json
        print("response is",qids,len(qids))


        url = f"http://{MOI_IP}:{MOI_PORT}/getemails"

        payload = json.dumps({
          "QIDS": qids
        })
        headers = {
          'Content-Type': 'application/json'
        }
        print("Sending request to moi to get emails",url)
        response = requests.request("POST", url, headers=headers, data=payload)


        data = json.loads(response.text)
        emails=data["emails"]
        print(emails)


        for receiver_email in emails:            
            print(receiver_email)
            receiver_email=decrypt(receiver_email)
            print("After dec",receiver_email)
            receiver_email=receiver_email.decode("utf-8") 
            print(receiver_email)
            message = """\
            Subject: COVID Test

            Hello, you should get tested."""

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)            


        return "Emails sent to "+str(emails)
    return render_template('searchemail.html')


@app.route('/search/', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        QID = str(request.form['qid'])                
        
        if len(QID)!=0:
            conn = get_db_connection()
            cur = conn.cursor()
            select_qid_query="SELECT * FROM health_status where qatarid like '"+QID+"'"
            cur.execute(select_qid_query)        
            persons = cur.fetchall()
            cur.close()
            conn.close()            
            return render_template('index.html', persons=persons)

        


    return render_template('search.html')


if __name__=="__main__":
    # app.run(host="0.0.0.0",port=5002)  
    socketio.run(app,host='0.0.0.0',port=5002)  
