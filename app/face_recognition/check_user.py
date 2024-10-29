import cv2, face_recognition, ast 
import numpy, pandas


df = pandas.read_csv("app/face_recognition/User.csv") # Đọc file CSV

Encode_List = df["face_encoding"].apply(lambda x: numpy.array(ast.literal_eval(x))) # Chuyển đổi cột 'face_encoding' thành danh sách các mảng NumPy

def check_user(Path):
    curImg = cv2.imread(Path)
    curImg = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)

    EncodeCurImg = face_recognition.face_encodings(curImg)[0] # Mã hóa khuôn mặt của ảnh hiện tại

    FaceDis = face_recognition.face_distance(Encode_List.tolist(), EncodeCurImg) # Tính khoảng cách giữa mã hóa hiện tại và các mã hóa đã lưu

    MatchIndex = numpy.argmin(FaceDis) # Tìm chỉ số của khuôn mặt gần nhất
    
    if FaceDis[MatchIndex] < 0.5: # Kiểm tra xem khoảng cách có nhỏ hơn ngưỡng 0.5 không
        return df.iloc[MatchIndex]["id"]
    else:
        return "Không tìm thấy người dùng"


print(check_user("app/face_recognition/image/2.jpg"))
