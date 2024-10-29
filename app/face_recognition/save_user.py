import cv2, os, face_recognition
import numpy, pandas

path="pic"
images=[]
ID_USERS=[]
myList=os.listdir(path) #doc tat ca cac file trong pic
cnt=1

for file in myList:
    curImg=cv2.imread(os.path.join(path,file))#doc anh
    images.append(curImg)
    ID_USERS.append(cnt)
    cnt+=1

def Encoder (images):
    encodeList=[]
    for image in images:
        image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        encodeList.append(face_recognition.face_encodings(image)[0])
    return encodeList

Encode_List_Users=Encoder(images)
Encode_List_Users_str = [numpy.array2string(encoding, separator=', ') if encoding is not None else None for encoding in Encode_List_Users]

df=pandas.DataFrame({"face_encoding":Encode_List_Users_str,"id":ID_USERS})
df.to_csv("User.csv",index=False)
