#!/usr/bin/env python
# coding: utf-8

# In[75]:


from PIL import Image
from datetime import datetime

import numpy as np
import cv2
import pickle

from math import sqrt

import os
import shutil

import time
from ultralytics import YOLO
import psycopg2


positive_qid="92667137558"



model = YOLO("weights/best.pt") # pass any model type


skipcount=3



# Focal length
F = 615
safe_dist=100
# In[73]:



        
def get_db_connections():
    
    conn = psycopg2.connect(
        host="localhost",
        database="mall",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])
    return conn



# among the persons in the frame, detect the ones that are close by
def detect_close_persons(people_dict):
    print("In detect_close_persons")
    isClose=False
    
    dict_breach_details={}
    list_breach_details=[]

    close_objects = set()
    for i in people_dict.keys():
        for j in people_dict.keys():
            if i < j:
                x_i=people_dict[i]["position"][0]
                y_i=people_dict[i]["position"][1]
                dist_i=people_dict[i]["position"][2]

                x_j=people_dict[j]["position"][0]
                y_j=people_dict[j]["position"][1]
                dist_j=people_dict[j]["position"][2]

                
                dist = sqrt(pow(x_i-x_j,2) + pow(y_i-y_j,2) + pow(dist_i-dist_j,2))
                print("distance between ",i," and ",j," is ",dist,"\n")

                # Check if distance less than 2 metres or 200 centimetres

                if dist < safe_dist:                    
                    close_objects.add(i)
                    close_objects.add(j)      
                    isClose=True              
                    temp_dict={}
                    # can we convert the distance to feet
                    # dist_feet=int(0.0328084*dist)
                    temp_dict["distance"]=int(dist)
                    temp_dict["employee_1"]=i
                    temp_dict["employee_2"]=j
                    list_breach_details.append(temp_dict)

                else:
                    pass
                    # breach_happened.append(False)  
    dict_breach_details["breach_data"]=list_breach_details
    


              
    return close_objects,dict_breach_details,isClose


# In[ ]:





# In[104]:


    
# cap = cv2.VideoCapture("res/videoplaybackcamcafe.mp4")   

cap = cv2.VideoCapture("res/videoplaybackcamcafe.mp4")   

# cap = cv2.VideoCapture(0)

# any one of the two lines above






ret, frame = cap.read()
h=frame.shape[0]
w=frame.shape[1]
x_start=0
y_start=0

print(h,w,x_start,y_start)


count_frames=0

conn=get_db_connections()
cur=conn.cursor()

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    count_frames+=1
    if count_frames%skipcount==0:
        
        


        x=x_start
        y=y_start
        w=w
        h=h


        print("In detect_persons",frame.shape)
        print("x,y,w,h = ",x,y,w,h)



        startX=x
        startY=y
        endX=startX+w
        endY=startY+h


        # cv2.rectangle(frame, (startX, startY), (endX, endY), (0,250,50), 2)

        roi=frame[startY:endY, startX:endX]
        print("ROI shape = ",roi.shape)
        results = model.predict(source=roi,save=False)  # save plotted images
        print(results[0].boxes.boxes.shape)





        # (h, w) = frame.shape[:2]
        (height, width) = roi.shape[:2]
        channels=roi.shape[2]


        boxes_xyxy=results[0].boxes.xyxy.detach().numpy()
        classes=results[0].boxes.cls

        people_boxes=[]
        for i in range(classes.shape[0]):
            clas=classes[i]
            if clas !=0:
                continue
            box_xyxy=boxes_xyxy[i]
            box_xyxy=box_xyxy.astype(int)
            people_boxes.append(box_xyxy)


        print("pboxes",people_boxes)


        count_people=0
        people_dict={}
        for i in range(len(people_boxes)):

            startX, startY, endX, endY = people_boxes[i]


            
            height=round(endY-startY,4)
            # Distance from camera based on triangle similarity
            distance=(165*F)/height

            # Mid point of bounding box
            x_mid = round((startX+endX)/2,4)
            y_mid = round((startY+endY)/2,4)

            # Mid-point of bounding boxes (in cm) based on triangle similarity technique
            x_mid_cm = (x_mid * distance) / F
            y_mid_cm = (y_mid * distance) / F



            
            people_dict[count_people]={}
            people_dict[count_people]["coords"]=(startX, startY, endX, endY)
            people_dict[count_people]["position"]=(x_mid_cm,y_mid_cm,distance)
            count_people+=1

        close_objects,dict_breach_details,isClose = detect_close_persons(people_dict)

        print("************************************")
        print("Number of people is", count_people, people_dict)
        print("************************************")
        print("Closeness",isClose)


        if isClose:
            close_qids=[]
            for i in range(count_people):
                startX, startY, endX, endY=people_dict[i]["coords"]
                person_of_interest=frame[startY:endY, startX:endX]


                import requests
                url=f"http://{os.environ['MOI_IP']}:{os.environ['MOI_PORT']}/searchbyFE"
                cv2.imwrite("test.jpg",person_of_interest)
                imgg=cv2.imread('test.jpg')

                scale_percent = 30 # percent of original size
                width = int(imgg.shape[1] * scale_percent / 100)
                height = int(imgg.shape[0] * scale_percent / 100)
                dim = (width, height)
                imgg = cv2.resize(imgg, dim, interpolation = cv2.INTER_AREA)





                _, img_enc=cv2.imencode('.jpg',imgg)
                content_type="image/jpeg"
                headers={"content-type": content_type}
                
                response=requests.post(url,data=img_enc.tostring(),headers=headers)
                time.sleep(5)
                print(response)
                
                print("resp is",response.json())
                data=response.json()
                qid=data["qids"]
                if qid=="Unknown" or qid=="None":
                    continue
                close_qids.append(qid)


        print("Close qids are ",close_qids)
        if positive_qid in close_qids:
            # we need to store them all
            close_qids.remove(positive_qid)
            for each_qid in close_qids:
                # insert query to put in database
                insert_sql="""INSERT INTO contacttracing( QatarID1, QatarID2)
                    VALUES(%s,%s);"""
                print("Going to insert",insert_sql)
                cur.execute(insert_sql,(positive_qid,each_qid))
                conn.commit()



                
                

        
        for i in range(count_people):


            startX, startY, endX, endY=people_dict[i]["coords"]
            startX, startY, endX, endY=int(startX), int(startY), int(endX), int(endY)
            print(startX, startY, endX, endY)
            crop_img = frame[startY:endY, startX:endX]
            print("Shape of cropped image is ",crop_img.shape)




            # this part to mark boxes on people              
            COLOR = (0,255,0)
            if i in close_objects:                    
                COLOR=(0,0,255)
            label=str(i)
            cv2.rectangle(frame, (startX, startY), (endX, endY), COLOR, 2)

            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR, 2)



        if isClose:
            cv2.putText(frame,str(datetime.now()),(10,20), cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,0),2,cv2.LINE_AA)

#         cv2.imwrite('outs/frame'+str(count_frames)+".jpeg",frame)  
        cv2.imshow('outs/frame'+str(count_frames),frame)          
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
        


# In[ ]:

