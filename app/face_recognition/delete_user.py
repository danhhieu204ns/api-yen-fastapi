import pandas as pd

df=pd.read_csv("app/face_recognition/User.csv")

def delete_user_by_id(user_id):
    global df
    if user_id in df["id"].values:
        df=df[df["id"]!=user_id]
        df.to_csv("app/face_recognition/User.csv",index=False)
        print("User deleted successfully")
    else:
        print("User not found")

delete_user_by_id(7)