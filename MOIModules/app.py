import face_recognition
import cv2
from flask import jsonify
from cryptography.fernet import Fernet
import pickle

import numpy as  np

import random
import os
import psycopg2

from flask import Flask, render_template, request, url_for, redirect,Response
from flask_cors import CORS, cross_origin

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage


import lib
NUM=3
# this part for encryption
import random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from flask_socketio import SocketIO



import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import torch.utils.data as data_utils
import sys
import torch.optim as optim
from torch.optim import lr_scheduler
from timeit import default_timer as timer
import pickle
import time
#import lib_prune
import copy
import numpy as np
#import matplotlib.pyplot as plt



# key = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))


def decrypt(encrypted_string):
    key=b'abcdefghjkloiupu'
    iv = b'qwertyuioplkjhgf'


    aes = AES.new(key, AES.MODE_EAX, iv)
    str_tmp = b64decode(encrypted_string.encode('utf-8'))
    # print("tmp",str_tmp)
    str_dec = aes.decrypt(str_tmp)
    # print("dec",str_dec)
    return str_dec

def encrypt(unencrypted_string):
    key=b'abcdefghjkloiupu'
    iv = b'qwertyuioplkjhgf'
    aes = AES.new(key, AES.MODE_EAX, iv)
    print("Encrypting",unencrypted_string)
    data=bytes(unencrypted_string,'utf-8')
    print("utf-8",data)
    encd = aes.encrypt(data)
    print("encd",encd)
    mret = b64encode(encd).decode('utf-8')
    print("mret",mret)
    return mret


# def encrypt(unencrypted_string):

#     new_chars=[]
#     for ch in unencrypted_string:
#         x = chr(ord(ch) + NUM)
#         new_chars.append(x)
#     new_chars="".join(char for char in new_chars)
#     return new_chars
#     # return fernet._encrypt_from_parts(unencrypted_string.encode(), 0,b'\xbd\xc0,\x16\x87\xd7G\xb5\xe5\xcc\xdb\xf9\x07\xaf\xa0\xfa')


with open(r"key.pickle", "rb") as input_file:
    key=pickle.load(input_file)
print(key)
fernet = Fernet(key)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app)

# new code get_encodings_from_registration
name_list,enc_list,qid_list=lib.get_encodings_from_registration()
print("list of enc",enc_list)
known_face_encodings = enc_list
known_face_names = name_list
known_qatar_ids=qid_list

with open(r"key.pickle", "rb") as input_file:
    key=pickle.load(input_file)
print("enc  key is",key)


def generate_qid():
    n = 11
    qid=''.join(["{}".format(random.randint(0, 9)) for num in range(0, n)])
    return qid




def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='moi',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM registration;')
    persons = cur.fetchall()
    persons=list(persons)
    for i in range(len(persons)):
        persons[i]=list(persons[i])
        print("Email is  ",persons[i][3])
        decrـemail=decrypt(persons[i][3])
        decrـemail=decrـemail.decode("utf-8")
        persons[i][3]=decrـemail
        print(decrـemail)
    cur.close()
    conn.close()
    return render_template('index.html', persons=persons)






@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        first_name = str(request.form['first_name'])
        last_name = str(request.form['last_name'])
        tel_num = str(request.form['tel_num'])
        email_id = str(request.form['email_id'])
        dob = str(request.form['dob'])
        f = request.files['avatar']
        f.save(secure_filename(f.filename))
        print("Ok got it",email_id)
        
        conn = get_db_connection()
        cur = conn.cursor()

        select_query="SELECT * FROM registration where first_name like %s and last_name like %s and dob = %s"
        print(select_query)
        cur.execute(select_query, (first_name,last_name,dob))
        records = cur.fetchall()

        if len(records)!=0:
            print("Person present")
        else:
            print("New entry")
            possible_qid=str(generate_qid())
            print(possible_qid,"length is",len(possible_qid))
            select_qid_query="SELECT * FROM registration where qatarid like '"+possible_qid+"'"
            print(select_qid_query)
            cur.execute(select_qid_query)
            records = cur.fetchall()
            if len(records)!=0:
                print("Try again, qid exists")
            else:
                print(possible_qid,"is your new qid")
                email_id=encrypt(email_id)
                print("The Encrypted email_id is ",email_id)


                # main work is to insert 
                whole_path=f.filename               
                print("Whole path to image=",whole_path)
                face = face_recognition.load_image_file(whole_path)
                face_encoding = face_recognition.face_encodings(face)[0]
                print("Data type of face encoding is",face_encoding.dtype) 
                print("face encoding shape= ",face_encoding.shape)
                face_encoding_str=str(face_encoding)
                print("Data type of face encoding is",face_encoding.dtype) 
                # print(first_name+last_name+tel_num+dob+possible_qid+face_encoding_str)
                insert_sql = """INSERT INTO registration(first_name,last_name,phone_number,email_id,dob,Qatarid,encoding)
                    VALUES(%s,%s,%s,%s,%s,%s,%s);"""
                cur.execute(insert_sql, (first_name,last_name,tel_num,email_id,dob,possible_qid,face_encoding_str))
                conn.commit()

                print("Added succesfully")



        # conn = get_db_connection()
        # cur = conn.cursor()
        # cur.execute('INSERT INTO books (title, author, pages_num, review)'
        #             'VALUES (%s, %s, %s, %s)',
        #             (title, author, pages_num, review))
        # conn.commit()
        # cur.close()
        # conn.close()
        return redirect(url_for('index'))

    return render_template('create.html')



@app.route('/searchbyQID/', methods=('GET', 'POST'))
@cross_origin()
def searchbyQID():
    if request.method == 'POST':
        data = request.json
        print(data.get('QID'))
        QID=str(data.get('QID'))
        

        if len(QID)!=0:
            conn = get_db_connection()
            cur = conn.cursor()
            select_qid_query="SELECT * FROM registration where qatarid like '"+QID+"'"
            cur.execute(select_qid_query)        
            persons = cur.fetchall()
            if len(persons)==1:
                data["exists"]="True"
            else:
                data["exists"]="False"
            return data




@app.route('/getemails/', methods=('GET', 'POST'))
@cross_origin()
def getemails():
    if request.method == 'POST':
        data = request.json
        print(data.get('QIDS'))
        QIDS=data.get('QIDS')
        print("QIDs are",QIDS,len(QIDS))
        

        if len(QIDS)!=0:
            emailIDs=[]
            for QID in QIDS:
                conn = get_db_connection()
                cur = conn.cursor()
                select_qid_query="SELECT email_id FROM registration where qatarid like '"+QID+"'"
                print("Query is ",select_qid_query)
                cur.execute(select_qid_query)        
                persons = cur.fetchall()
                if len(persons)==1:
                    email_ID=persons[0][0]
                    print(email_ID)
                    emailIDs.append(email_ID)                    
                else:
                    print("No email")
            response={}
            response["emails"]=emailIDs
            jsonify(response)
            return response




@app.route('/search/', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        first_name = str(request.form['first_name'])
        last_name = str(request.form['last_name'])        
        dob = str(request.form['dob'])
        QID = str(request.form['QID'])        

        if len(QID)!=0:
            conn = get_db_connection()
            cur = conn.cursor()
            select_qid_query="SELECT * FROM registration where qatarid like '"+QID+"'"
            cur.execute(select_qid_query)        
            persons = cur.fetchall()
            cur.close()
            conn.close()            
            return render_template('index.html', persons=persons)

        # lets use name and dob
        conn = get_db_connection()
        cur = conn.cursor()
        select_query="SELECT * FROM registration where first_name like %s and last_name like %s and dob = %s"
        print(select_query)
        cur.execute(select_query, (first_name,last_name,dob))
        persons = cur.fetchall()
        cur.close()
        conn.close()    
        return render_template('index.html', persons=persons)


    return render_template('search.html')

import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader,Dataset
from PIL import Image

import nn_live 

def pre_image(image_path,model):
   img = Image.open(image_path)
   mean = [0.485, 0.456, 0.406] 
   std = [0.229, 0.224, 0.225]
   transform = transforms.Compose([
                                    transforms.Resize((32,32)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean = (0.1307,), std = (0.3081,))])

   
   # get normalized image
   img_normalized = transform(img).float()
   img_normalized = img_normalized.unsqueeze_(0)
   # input = Variable(image_tensor)
   img_normalized = img_normalized.to(device)
   # print(img_normalized.shape)
   with torch.no_grad():
      model.eval()  
      output =model(img_normalized)
     # print(output)
      index = output.data.cpu().numpy().argmax()
      print("Status=",index)
      classes = ["live","not live"]
      class_name = classes[index]
      return class_name
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
@app.route('/searchbyFE/', methods=('GET', 'POST'))
@cross_origin()
def searchbyFaceEncoding():
    if request.method == 'POST':
        r = request
        print("r",r)
        # convert string of image data to uint8
        nparr = np.fromstring(r.data, np.uint8)
        # decode image
        rgb_small_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite("mg.jpeg",rgb_small_frame)
        image_path="mg.jpeg"

        # let us do liveness detection here
        
        num_classes=10
        model_ft = nn_live.LeNet5(num_classes).to(device)
        num_epochs=10
        model_state_path="models/simple_LeNet5_Liveness_"+str(num_epochs)+".pt"
        model_ft.load_state_dict(torch.load(model_state_path,map_location=device))
        clss=pre_image(image_path,model_ft)
        print("Status of image",clss)




        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        got_qids=[]
        # print("fes  from image are ",face_encodings)
        # print("known_face_encodings",known_face_encodings)
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            qid="Unknown"
            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            print(face_encoding[0].shape,known_face_encodings[0].shape)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                qid=known_qatar_ids[best_match_index]

            face_names.append(name)
            got_qids.append(qid)


        print("Face names",face_names)
        print("qids",got_qids)
        if len(got_qids)==0:
            response = {
            'qids':"None",    
                }
        elif got_qids[0]=="Unknown":
            response = {
            'qids':"Unknown",    
                }
        else:        
            response = {
            'qids':str(got_qids[0]),    
                }

        # encode response using jsonpickle
        response_pickled = jsonify(response)
        return response_pickled


    response={
            'qids':"None",    
                }
    response_pickled = jsonify(response)
    return response_pickled

        # return Response(response=response_pickled, status=200, mimetype="application/json")

   






if __name__=="__main__":
    # app.run(host="0.0.0.0",port=5001,debug=True)  
    socketio.run(app,host='0.0.0.0',port=5001,debug=True)  