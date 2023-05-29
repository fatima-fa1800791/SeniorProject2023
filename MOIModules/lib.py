import face_recognition
import cv2
import numpy as np
import pickle
import psycopg2
conn = psycopg2.connect("dbname=moi user=moi")
cur = conn.cursor()
# This code to DO encoding saperatly and before the actual running time

# To load all images from a folder
import os


import psycopg2



# def get_encodings_from_db():
#     name_list=[]
#     encoding_list=[]

#     conn = psycopg2.connect("dbname=facedb user=user")
#     # Open a cursor to perform database operations
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM face_encodings")
#     records = cur.fetchall()

#     # process string to arrays
#     for rec in records:
#         name=rec[0]
#         num=rec[1]
#         enc_str=rec[2]
#         print("original string ",enc_str)
#         enc_str=enc_str.replace("]","")
#         enc_str=enc_str.replace("[","")
#         enc_str=enc_str.replace("\n","")
#         enc_str = " ".join(enc_str.split())

#         items=enc_str.split(" ")
#         # print(enc_str)
#         # print(items[:10])
#         new_enc=[]
#         for i in items:
#             # print("converting ",i)
#             new_i=float(i)
#             new_enc.append(new_i)
#         # print(items[:3])
#         # print(new_enc[:3])
#         new_enc=np.array(new_enc)
#         # print(new_enc.shape)
        
#         # print(name,num,len(enc_str))
#         name_list.append(name)
#         encoding_list.append(new_enc)
        

#     return name_list,encoding_list


def get_encodings_from_registration():
    name_list=[]
    encoding_list=[]
    qid_list=[]

    conn = psycopg2.connect("dbname=moi user=moi")
    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("SELECT * FROM registration")
    records = cur.fetchall()

    # process string to arrays
    for rec in records:
        fname=rec[0]
        lname=rec[1]
        dob=rec[4]
        qid=rec[5]
        enc_str=rec[6]
        # print("original string ",enc_str)
        enc_str=enc_str.replace("]","")
        enc_str=enc_str.replace("[","")
        enc_str=enc_str.replace("\n","")
        enc_str = " ".join(enc_str.split())

        items=enc_str.split(" ")
        # print(enc_str)
        # print(items[:10])
        new_enc=[]
        for i in items:
            # print("converting ",i)
            new_i=float(i)
            new_enc.append(new_i)
        # print(items[:3])
        # print(new_enc[:3])
        new_enc=np.array(new_enc)
        # print(new_enc.shape)
        
        # print(name,num,len(enc_str))
        name_list.append(fname+" "+lname)
        encoding_list.append(new_enc)
        qid_list.append(qid)
        

    return name_list,encoding_list,qid_list    


def get_health_stataus(this_qid):
    '''
    get positive or negative
    '''
    select_hlth_query="SELECT covid_status FROM health_status where qatarid like '"+this_qid+"'"
    print(select_hlth_query)
    cur.execute(select_hlth_query)
    
    records = cur.fetchall()
    if len(records)==0:
        return "Unknown"
    print(records)
    return records[0][0]

def check_if_enc_present(enc_str):
    '''
    return true if enc present
    return false if enc not present
    '''
    select_query="SELECT * FROM face_encodings where encoding=%s"
    print(enc_str)
    cur.execute(select_query, (enc_str))
    records = cur.fetchall()
    if len(records)==0:
        return False
    else:
        return True

        # empty so no such encodings present
        # add it


# nm_l,enc_l=get_encodings_from_db()    
# print(enc_l)
# print(nm_l)