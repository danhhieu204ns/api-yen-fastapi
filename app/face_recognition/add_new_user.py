import cv2, face_recognition
import numpy, pandas


df = pandas.read_csv("app/face_recognition/User.csv")

def add_new_user(path, user_id):
    global df
    new_image = cv2.imread(path)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    new_encoding = face_recognition.face_encodings(new_image)[0]

    new_encoding_str = numpy.array2string(new_encoding, separator=', ')  # Chuyển đổi thành chuỗi
        
    new_row = pandas.DataFrame({"face_encoding": new_encoding_str, "id": [user_id]}) # Tạo DataFrame mới cho người dùng mới
        
    df = pandas.concat([df, new_row], ignore_index=True) # Thêm hàng mới vào DataFrame hiện có

    df.to_csv("app/face_recognition/User.csv", index=False) # Lưu lại vào CSV
    print(f"Đã thêm người dùng mới với ID: {user_id}")

