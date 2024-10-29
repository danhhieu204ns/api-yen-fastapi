import cv2, os, face_recognition
import numpy, pandas


df=pandas.read_csv("User.csv")

def update_face_encodings(img_path,user_id):
    if user_id not in df['id'].values:
        print(f"Không tìm thấy người dùng có ID: {user_id}")
        return
    new_image = cv2.imread(img_path)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    new_encodings = face_recognition.face_encodings(new_image)[0]
    new_encoding_str = numpy.array2string(new_encodings, separator=', ')
    df.loc[df['id'] == user_id, 'face_encoding'] = new_encoding_str

    df.to_csv("User.csv", index=False)
    print(f"Đã cập nhật mã hóa cho người dùng với ID: {user_id}")