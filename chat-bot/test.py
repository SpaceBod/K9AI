import requests, re
import pyttsx3 as tts
import speech_recognition
from playsound import playsound as sound
import datetime
from music import *
import struct
import face_recognition
import cv2
import os
import glob
import numpy as np
import pickle

def add_face(person):
    cap = cv2.VideoCapture(0)
    _, image = cap.read()
    image_path = f"faces/{person}.jpg"
    cv2.imwrite(image_path, image)
    print(f"Face captured and saved as {image_path}")

