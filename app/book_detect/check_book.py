import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Tải mô hình đã lưu
model = load_model('app/my_model.h5')

# Hàm dự đoán cuốn sách từ ảnh đầu vào
def predict_book_cover(img_path, model, class_names):
    # Tải và tiền xử lý ảnh
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Thêm chiều batch
    img_array /= 255.0  # Chuẩn hóa giá trị pixel
    # Dự đoán với mô hình
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=-1)
    # Trả về tên của lớp dự đoán
    return class_names[predicted_class[0]]

# Danh sách tên các lớp (điền tên lớp của bạn vào đây)
class_names = ['1', '8', '3', '4', '5', '6']

def predict_book(img_path):

    predicted_book = predict_book_cover(img_path, model, class_names)

    return predicted_book

