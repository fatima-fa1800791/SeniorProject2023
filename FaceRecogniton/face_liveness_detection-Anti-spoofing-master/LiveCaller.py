import face_recognition
import cv2
import numpy as np
import pickle
import os
import time
import json
from datetime import datetime, timezone, timedelta

import psycopg2

import RPi.GPIO as GPIO
import time
import tkinter as tk
from tkinter import *

# Set GPIO numbering mode
# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False) 


# for cd rom gate
gate1_p1 = 19 # port number 35
GPIO.setup(gate1_p1, GPIO.OUT)

gate1_p2 = 13 # port number 33
GPIO.setup(gate1_p2, GPIO.OUT)

def close_gate():
    GPIO.output(gate1_p1,1)
    GPIO.output(gate1_p2,0)
    time.sleep(1.5) 
    GPIO.output(gate1_p1,0)
    GPIO.output(gate1_p2,0)
    


def open_gate():
    GPIO.output(gate1_p1,0)
    GPIO.output(gate1_p2,1)
    time.sleep(3) 
    GPIO.output(gate1_p1,0)
    GPIO.output(gate1_p2,0)

# Set pin 11 as an output, and define as servo1 as PWM pin
#GPIO.setup(11,GPIO.OUT)
#servo1 = GPIO.PWM(11,50) # pin 11 for servo1, pulse 50Hz

# Start PWM running, with value of 0 (pulse off)
#servo1.start(0)

# Loop to allow user to set servo angle. Try/finally allows exit
# with execution of servo.stop and GPIO cleanup :)

def getDutyCFromAngle(angl):
    # angl is a float
    return 2+(angl/18)




import cv2, queue, threading, time

# bufferless VideoCapture
class VideoCapture:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()
    
       
def get_db_connections():
   
    conn = psycopg2.connect(
        host= os.environ["MALL_SERVER_IP"], # ip address of mall laptop/server/Meznas sisters laptop
        database="mall",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])
    return conn

# 1 for Meznas system


######################################################################
####################### liveness test ################################
######################################################################



import random 
import cv2
import imutils
import f_liveness_detection
import questions





def show_image(cam,text,color = (0,0,255)):
    ret, im = cam.read()
    im = imutils.resize(im, width=720)
    #im = cv2.flip(im, 1)
    cv2.putText(im,text,(10,50),cv2.FONT_HERSHEY_COMPLEX,1,color,2)
    return im

def check_spoof():
    # parameters 
    COUNTER, TOTAL = 0,0
    counter_ok_questions = 0
    counter_ok_consecutives = 0
    limit_consecutives = 2
    limit_questions = 3
    counter_try = 0
    limit_try = 15


    for i_questions in range(0,limit_questions):
        # genero aleatoriamente pregunta
        index_question = random.randint(0,1)
        question = questions.question_bank(index_question)
        
        im = show_image(cam,question)
        cv2.imshow('liveness_detection',im)
        if cv2.waitKey(1) &0xFF == ord('q'):
            break 

        for i_try in range(limit_try):
            # <----------------------- ingestar data 
            ret, im = cam.read()
            im = imutils.resize(im, width=720)
            im = cv2.flip(im, 1)
            # <----------------------- ingestar data 
            TOTAL_0 = TOTAL
            out_model = f_liveness_detection.detect_liveness(im,COUNTER,TOTAL_0)
            TOTAL = out_model['total_blinks']
            COUNTER = out_model['count_blinks_consecutives']
            dif_blink = TOTAL-TOTAL_0
            if dif_blink > 0:
                blinks_up = 1
            else:
                blinks_up = 0

            challenge_res = questions.challenge_result(question, out_model,blinks_up)

            im = show_image(cam,question)
            cv2.imshow('liveness_detection',im)
            if cv2.waitKey(1) &0xFF == ord('q'):
                break 

            if challenge_res == "pass":
                im = show_image(cam,question+" : ok")
                cv2.imshow('liveness_detection',im)
                if cv2.waitKey(1) &0xFF == ord('q'):
                    break

                counter_ok_consecutives += 1
                if counter_ok_consecutives == limit_consecutives:
                    counter_ok_questions += 1
                    counter_try = 0
                    counter_ok_consecutives = 0
                    break
                else:
                    continue

            elif challenge_res == "fail":
                counter_try += 1
                show_image(cam,question+" : fail")
            elif i_try == limit_try-1:
                break
                

        if counter_ok_questions ==  limit_questions:
            while True:
                im = show_image(cam,"LIFENESS SUCCESSFUL",color = (0,255,0))
                cv2.imshow('liveness_detection',im)
                return "Alive"
                if cv2.waitKey(1) &0xFF == ord('q'):
                    break
        elif i_try == limit_try-1:
            while True:
                im = show_image(cam,"LIFENESS FAIL")
                cv2.imshow('liveness_detection',im)
                return "Spoof"
                if cv2.waitKey(1) &0xFF == ord('q'):
                    break
            break 

        else:
            continue




while True:


    # instanciar camara
    cv2.namedWindow('liveness_detection')
    cam = cv2.VideoCapture(0)

    while True:
        spoof_status=check_spoof()
        print("Status of face",spoof_status)
        if spoof_status=="Alive":
            cam.release()
            cv2.destroyAllWindows()
            break
        else:            
            ROOT = tk.Tk()
            ROOT.geometry("1700x1700")
            msg="Spoof"
            bg="red"
            canvas= Canvas(ROOT, width= 1700, height= 1700, bg=bg)
            canvas.create_text(700, 400, text=msg, fill="white", font=('TimesNewRomans 100 bold'))
            canvas.pack()

            ROOT.title(msg)            
            ROOT.update()
            time.sleep(2)             
            ROOT.destroy()            
            

    ######################################################################
    ################### end of liveness test #############################
    ######################################################################







    #video_capture = cv2.VideoCapture(0)
    video_capture = VideoCapture(0)
    #video_capture.set(cv2.CAP_PROP_BUFFERSIZE,1)
    process_this_frame=True

    print("Closing gate")
    close_gate()

    conn=get_db_connections()
    print("connected")
    cur=conn.cursor()
    while True:
       
        print("Closing gate")
        
        
        
        
        
        # set up correct motor position as closed
        angle = 0.0
        #servo1.ChangeDutyCycle(getDutyCFromAngle(angle))
       
        # Grab a single frame of video
        #ret, frame = video_capture.read()
        frame = video_capture.read()
        
        print("frame",frame.shape)
        
        
        # print("shape",frame.shape)
        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            
            
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame=small_frame
            # rgb_small_frame = small_frame[:, :, ::-1]
           
            # try to send the whole image
            import requests
            url=f"http://{os.environ['MOI_IP']}:{os.environ['MOI_PORT']}/searchbyFE"
            cv2.imwrite("test.jpg",rgb_small_frame)
            imgg=cv2.imread('test.jpg')
            _, img_enc=cv2.imencode('.jpg',imgg)
            content_type="image/jpeg"
            headers={"content-type": content_type}
           
            response=requests.post(url,data=img_enc.tostring(),headers=headers)
            print(response)
           
            print("resp is",response.json())
            time.sleep(1)
           
           
            data=response.json()
            qid=data["qids"]
            if qid=="None":
                print("No face")
                video_capture.cap.release()
                cv2.destroyAllWindows()
                print("Go and check liveness next time")        
                break
                
            if qid=="Unknown" or qid=="None":
               
                print("Please remove mask/register yourself")
                font = cv2.FONT_HERSHEY_DUPLEX
                msg="Please remove mask/register yourself"
                ROOT = tk.Tk()
                ROOT.geometry("1700x1700")
                canvas=Canvas(ROOT, width= 1700, height= 1700, bg="yellow")

                canvas.create_text(700, 300, text="Stop", fill="red", font=('TimesNewRomans 100 bold'))
                canvas.create_text(700, 500, text="Please Remove The Face Mask / Sunglasses", fill="red", font=('TimesNewRomans 60 bold'))
                canvas.pack() 
                ROOT.title(msg)
               
                ROOT.update()
    #            LABEL=Label(ROOT,text=msg)
    #            LABEL.place(x=70,y=70)
    #            LABEL.pack()

                #cv2.putText(frame, msg, (50, 50), font, 1.0, (255, 255, 255), 1)
                time.sleep(1)  
                ROOT.destroy()
                
                
                # Release handle to the webcam
                video_capture.cap.release()
                cv2.destroyAllWindows()
                print("Go and check liveness")        
                break
            payload=json.dumps({
                "QID":qid
            })
            url=f"http://{os.environ['MOPH_IP']}:{os.environ['MOPH_PORT']}/getCovidStatusByQID"
            content_type="application/json"
            headers={"content-type": content_type}
            #print("sENDING moph",url,payload)
            response=requests.post(url,data=payload,headers=headers)
            data=response.json()
            #print(data)
            #print(data["covid_status"])
            cov_st=data["covid_status"]
            dt=datetime.now(timezone.utc)+timedelta(hours=3)
            #print(dt)
            insert_sql="""INSERT INTO mallentry(entry_time, covid_status, qatarid)
                VALUES(%s,%s,%s);"""
            #print("Going to insert",insert_sql)
            cur.execute(insert_sql,(dt,cov_st,qid))
            conn.commit()
            if data["covid_status"]=="Negative":
                print("Opening gate")
                bg="limegreen"
                msg="Welcome"
                angle = 90.0
                #servo1.ChangeDutyCycle(getDutyCFromAngle(angle))
                
                angle = 0.0
                #servo1.ChangeDutyCycle(getDutyCFromAngle(angle))
            else:

                bg="red"
                msg="Entry Denied for Covid19 infection"
            print(msg)
            ROOT = tk.Tk()
            ROOT.geometry("1700x1700")
            canvas= Canvas(ROOT, width= 1700, height= 1700, bg=bg)
            canvas.create_text(700, 400, text=msg, fill="white", font=('TimesNewRomans 100 bold'))
            canvas.pack()
            #label = tk.Label(
            #text="Deny"
            #fg="white"
            #bg="red"
            #width=50
            #height=50
            #}
            ROOT.title(msg)            
            ROOT.update()
            time.sleep(2)
            if data["covid_status"]=="Negative":
                open_gate()
                time.sleep(1)
                close_gate()            
             
            ROOT.destroy()
           
            #cv2.imshow('Video', frame)      
           
            '''
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            got_qids=[]
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
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    qid=known_qatar_ids[best_match_index]

                face_names.append(name)
                got_qids.append(qid)
        '''
        #`process_this_frame = not process_this_frame

        '''
        # Display the results
        for (top, right, bottom, left), name, this_qid in zip(face_locations, face_names,got_qids):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            health_status_report=lib.get_health_stataus(this_qid)
            # print("health status is ",health_status_report)

            if health_status_report=="Negative":
                box_color=(0, 255, 0)
            elif health_status_report=="Unknown":
                box_color=(255, 0, 0)
            else:
                box_color=(0, 0, 255)
           
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            print(name,this_qid,health_status_report)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        '''
        # Display the resulting image
        #cv2.imshow('Video', frame)
        #print("Showing on screen")
        #cv2.imwrite("saved/det_"+str(time.time())+".jpg",frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Release handle to the webcam
        video_capture.cap.release()
        cv2.destroyAllWindows()
        print("live ness check")
        break
