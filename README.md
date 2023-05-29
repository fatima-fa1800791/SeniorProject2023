# Automatic Health Status Verification System Implemented with Face Recognition – Based Access Control

###### This project proposes a verification system that uses face recognition to retrieve a visitor's most recent health state and an automatic gate to permit or prohibit admission based on that visitor's health status.
	 
###### Our use case for the well-being verification project was COVID-19 since it has many flaws, such as the need that users present their smart phones to enter public spaces. However, our verification system might also be used in many fields as a guest invitation checker for international conferences or as an employee attendance system.


## Installation

Use the package manager [pip] to install all those libraries:

```bash
pip install ..... 
face_recognition, cv2, flask, jsonify, cryptography.fernet, Fernet, pickle, numpy, np, random, os, psycopg2, Flask, render_template, request, url_for, redirect, Response, flask_cors, CORS, cross_origin, werkzeug.utils, secure_filename, werkzeug.datastructures, FileStorage, lib, Crypto.Cipher, AES, base64, b64encode, b64decode, flask_socketio, SocketIO, torch, torch.nn, torchvision, torchvision.transforms, torch.utils.data, sys, torch.optim, optim, lr_scheduler, timeit, default_timer, timer, pickle, time, copy, 


```
# Setup:

## 1. MOI sever:

```python

First time
__________________
createdb moi

psql -d moi

CREATE USER MOI WITH SUPERUSER PASSWORD 'moipass';

\q

psql -U moi 

export DB_USERNAME=moi
export DB_PASSWORD=moipass



Every time
__________________
export DB_USERNAME=moi
export DB_PASSWORD=moipass



cd MOIModules/
Python3 app.py

```
## 2. MOPH sever:

```python

First time
__________________
createdb moph

psql -d facedb

CREATE USER MOPH WITH SUPERUSER PASSWORD 'mophpass';

\q

psql -U moph 

export DB_USERNAME=moph
export DB_PASSWORD=mophpass

python init_db.py

# check IP address every time
export MOI_IP=192.168.43.61
export MOI_PORT=5001 

Every time
__________________

export DB_USERNAME=moph
export DB_PASSWORD=mophpass

# check IP address every time
export MOI_IP=192.168.10.4
export MOI_PORT=5001 


cd MOPHModules/
Python3 app.py


```
## 3. Venue sever setup:

```python

Every time
__________________

export DB_USERNAME=mall
export DB_PASSWORD=mallpass
 
#Check IP address Every time
export MOI_IP= 192.168.10.15
export MOI_PORT=5001
       
conda activate py37
 
 
cd Venue\/face_recog/new_stuff/phase3_mall_Flask/VENUEModules 

python3 app.py

```
## 4. Face recognition sever:

```python

To setup our server you need to write those in terminal window:

First time
psql
create user mall with superuser password 'mallpass';
\q
createdb mall



Each time
__________________

export DB_USERNAME=mall
export DB_PASSWORD=mallpass
#Check IP address Every time

export MOI_IP=192.168.0.100
export MOI_PORT=5001

#Check IP address Every time
export MOPH_IP=192.168.0.106
export MOPH_PORT=5002

#Check IP address Every time
export MALL_SERVER_IP=192.168.0.104

cd FaceRecogniton/face_liveness_detection-Anti-spoofing-master

python3 LiveCaller.py
```
# video analyzing
1. Make sure that you register all the people which appears in the video in the MOI database.

2. Upload the video in res file located at: Venue /phase2_video_analytics/res

3. Modify the TestDistanceDetectionWithMOI.py located at Venue/phase2_video_analytics/TestDistanceDetectionWithMOI :

line "25" to the infected case QID number and line "115" to the video name which you save in res folder. 

4. Open terminal and run the code located in:
python3 Venue /phase2_video_analytics/TestDistanceDetectionWithMOI


## Contributing

This code source has been developed and completed, by Fatima Arab and Mozna Al-Hajri. Would appreciate it if you could obtain our permission to use it. We would gladly respond to your inquiries through email: fa1800791@qu.edu.qa and ma1705176@student.qu.edu.qa:

## License

Qatar University - Computer Engineering Department 
