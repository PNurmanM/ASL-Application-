
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from flask import request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
io = SocketIO(app, cors_allowed_origins="*")


import tensorflow as tf
from tensorflow import keras
import sklearn
import joblib

# RECIEVE
# recieve {image, name}

# RETURN
# return a image with handpoints,
# return image prediction


import mediapipe as mp
import numpy as np
import cv2
import base64
import os
print(os.getcwd())

mph = mp.solutions.hands
mpd = mp.solutions.drawing_utils

hands = mph.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5
    )

def random_test():
    try:
        image = cv2.imread(r'C:\Users\nurma\Desktop\ASLFLASKREACT\backend\2.jpg')
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(e)


    cv2.imshow("us", rgbImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    hands = mph.Hands(
        static_image_mode = True,
        max_num_hands=2,
        min_detection_confidence=0.5
    )

    results = hands.process(rgbImage)
    hands.close()

    resultsData = results.multi_hand_landmarks

    for landmarkList in resultsData:
        mpd.draw_landmarks(image, landmarkList, mph.HAND_CONNECTIONS)

    cv2.imshow("us2", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



sequence = []
label_encoder = joblib.load(r'C:\Users\nurma\Desktop\ASLFLASKREACT\backend\label_encoder.pk1')
model = keras.models.load_model(r'C:\Users\nurma\Desktop\ASLFLASKREACT\backend\thirdGestureModel.keras')

def process_image(image_file):

    image_arr = np.frombuffer(image_file, np.uint8)
    image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)

    RvidData = cv2.resize(image, (480,480))

    vimage = cv2.cvtColor(RvidData, cv2.COLOR_BGR2RGB)
    vresult = hands.process(vimage)
    vdata = vresult.multi_hand_landmarks

    return vdata

    

@io.on("connect")
def showConnection():
    print("✅Front end connected")

@io.on("send_image")
def send_image(data):

    image_file = data.get("image_file")


    header, encoded = image_file.split(",", 1)
    decoded = base64.b64decode(encoded)

    if not image_file:
        return

    try:
        
        vdata = process_image(decoded)

        if vdata:
            predicted_label = ["hi"]
            for hand_landmark in vdata:
                landmarks = []
                for landmark in hand_landmark.landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])

                    sequence.append(landmarks)

                    if len(sequence) > 30:
                        sequence.pop(0)

                    if len(sequence) == 30:
                        x_test = np.expand_dims(sequence, axis=0)
                        prediction = model.predict(x_test)
                        predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])
                        print(predicted_label[0])
    

        io.emit("prediction", {"status": "success", "result": predicted_label[0]})
    except Exception as e:
        io.emit("prediction", {"status": "fail"})
    


if __name__ == "__main__":
    io.run(app, debug=True)