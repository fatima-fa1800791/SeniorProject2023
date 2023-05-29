import face_recognition
import cv2
import requests
import random
import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import json
from flask import jsonify


app = Flask(__name__)




def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='mall',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


# @app.route('/')
# def index():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM health_status;')
#     persons = cur.fetchall()
#     cur.close()
#     conn.close()
#     return render_template('index.html', persons=persons)







@app.route('/upload/', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':        
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_loc=os.path.join("uploaded_vids", filename)
        file.save(file_loc)
        QID = str(request.form['qid']) 
        import TestDistanceDetectionWithMOI
        TestDistanceDetectionWithMOI.search(vid_file_location=file_loc,positive_qid=QID)                 


        return "File uploaded successfully, analysis complete"

    return render_template('upload.html')

@app.route('/contacts/', methods=('GET', 'POST'))
def contacts():
    if request.method == 'POST':
        
        data = request.json                
        print(data)
        QID = str(data['QID'])  
        print("looking for qid",QID)
        
        if len(QID)!=0:

            conn = get_db_connection()
            cur = conn.cursor()
            select_qid_query="SELECT * FROM contacttracing where qatarid1 like '"+QID+"'"
            cur.execute(select_qid_query)        
            persons = cur.fetchall()
            contacts=set()
            for person in persons:
                contacts.add(person[1])
            
            contacts=list(contacts)
            print("contacts are ",contacts)
            cur.close()
            conn.close()            
            
            return jsonify(contacts)
    


        


    return "Not a post request, sorry"



# @app.route('/search/', methods=('GET', 'POST'))
# def search():
#     if request.method == 'POST':
#         QID = str(request.form['qid'])                
        
#         if len(QID)!=0:
#             conn = get_db_connection()
#             cur = conn.cursor()
#             select_qid_query="SELECT * FROM health_status where qatarid like '"+QID+"'"
#             cur.execute(select_qid_query)        
#             persons = cur.fetchall()
#             cur.close()
#             conn.close()            
#             return render_template('index.html', persons=persons)

        


#     return render_template('search.html')


if __name__=="__main__":
    app.run(host="0.0.0.0",port=5003,debug=True)    
