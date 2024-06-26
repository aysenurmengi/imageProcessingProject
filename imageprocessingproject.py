# -*- coding: utf-8 -*-
"""imageProcessingProject.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IEqOGxBulpkWKA0oHRM1McsklnL-SNAw
"""

import matplotlib.pyplot as plt
import pandas as pd
import cv2
import numpy as np
import tensorflow as tf
from sklearn import datasets
from sklearn.model_selection import train_test_split

def extract_features(image):
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    digit_moments = []
    bounding_boxes = []

    for contour in contours:
        moments = cv2.moments(contour)
        digit_moments.extend(list(moments.values()))
        x, y, w, h = cv2.boundingRect(contour)
        bounding_boxes.extend([x, y, w, h])

    return digit_moments, bounding_boxes

digits = datasets.load_digits()

moment_values = []
bounding_boxes = []

for digit in digits.images:
    digit_uint8 = cv2.convertScaleAbs(digit)
    moments, boxes = extract_features(digit_uint8)
    moment_values.append(moments)
    bounding_boxes.append(boxes)

max_moments_length = max(len(m) for m in moment_values)
max_boxes_length = max(len(b) for b in bounding_boxes)

moment_values_padded = [m + [0] * (max_moments_length - len(m)) for m in moment_values]
bounding_boxes_padded = [b + [0] * (max_boxes_length - len(b)) for b in bounding_boxes]

moment_values_array = np.array(moment_values_padded, dtype='float32')
bounding_boxes_array = np.array(bounding_boxes_padded, dtype='float32')

features = np.hstack((moment_values_array, bounding_boxes_array))
df_data = pd.DataFrame(features)

totalItems = df_data.shape[1]

X_train, X_test, y_train, y_test = train_test_split(
    df_data, digits.target, test_size=0.2, shuffle=False
)

model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(totalItems,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

model.fit(X_train, y_train, epochs=100)

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=2)

print('\nTest accuracy:', test_acc)