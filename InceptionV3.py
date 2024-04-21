# -*- coding: utf-8 -*-
"""InceptionV3(88%).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19BGNdU7kEwa8BYGmqY4PUQe2Bc7mAGa0
"""


#!mkdir -p ~/.kaggle

#!cp kaggle.json ~/.kaggle/

#!kaggle datasets download -d jehanbhathena/weather-dataset

import shutil

# Assuming the downloaded dataset is named 'weather_dataset.zip'
# and is in your current working directory
archive_filename = 'weather-dataset.zip'
destination_dir = 'weather-dataset'  # Replace with desired directory name

# Unzip the archive
shutil.unpack_archive(archive_filename, destination_dir, 'zip')

"""# Weather Image Recognition
## importing libraries
    firstly we should import libraries which are necessary for the model to function and for other segments such as data processing , result visualization etc.
"""

# Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing import image

# Pre-Trained Models
from tensorflow.keras.applications import InceptionV3, Xception, ResNet152V2, ResNet50V2, ResNet50

"""## Data Loading and Preprocessing
    we define the data_dir variable to specify the directory containing the image dataset. We then load the image dataset using tf.keras.preprocessing.image_dataset_from_directory function. Following that, we filter out any corrupted images from the dataset by iterating over each folder and deleting the corrupted images.
"""

data_dir = 'weather-dataset/dataset'

data = tf.keras.preprocessing.image_dataset_from_directory(data_dir)

#!pip install split-folders

import splitfolders
input_folder = "weather-dataset/dataset"
output = "data"
splitfolders.ratio(input_folder, output=output, seed=42, ratio=(.75, .25,))

import os
class_names = sorted(os.listdir(data_dir))
n_classes = len(class_names)
class_dis = [len(os.listdir(data_dir + "/" + name)) for name in class_names]
class_dis

"""**pie chart**"""

import plotly.express as px
fig = px.pie(names=class_names, values=class_dis, title="Class Distribution")
fig.update_layout({'title':{'x':0.2}})
fig.show()

"""**bar plot**"""

import seaborn as sns
plt.figure(figsize=(10,8))
sns.barplot(
    x=class_names,
    y=class_dis
)
plt.axhline(np.mean(class_dis), alpha=0.5, linestyle='--', color='k', label="Mean")
plt.title("Class Distribution")
plt.legend(fontsize=15)
plt.show()

"""## Data Augmentation and Generator
    In this segment, we create an ImageDataGenerator object datagen for data augmentation. The datagen is configured with various augmentation parameters such as rotation, width and height shift, shear, zoom, and horizontal flip. The images are also rescaled by dividing by 255. We then specify the image dimensions, batch size, and image shape. Finally, we create separate data generators for training and validation using the flow_from_directory method, which loads the images from the specified directory, performs data augmentation, and provides the images and their corresponding labels.
"""

# Create an ImageDataGenerator and do Image Augmentation
datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2)

height = 228
width = 228
channels = 3
batch_size = 32
img_shape = (height, width, channels)
img_size = (height, width)

train_data = datagen.flow_from_directory(
    data_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training')

val_data = datagen.flow_from_directory(
    data_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation')

num_classes = len(data.class_names)
print('.... Number of Classes : {0} ....'.format(num_classes))

"""### image visualization"""

# Define a function to see images
def show_img(data):
    plt.figure(figsize=(15, 15))
    for images, labels in data.take(1):
        for i in range(9):
            ax = plt.subplot(3, 3, i + 1)
            ax.imshow(images[i].numpy().astype("uint8"))
            ax.axis("on")

# Plot the images in the dataset
show_img(data)

"""## Training Model - InceptionV3

The code in this cell loads the pre-trained InceptionV3 model, freezes its layers, adds custom layers on top, and compiles the model.

The pre-trained VGG16 model is loaded using `tensorflow.keras.applications.InceptionV3` with the weights set to 'imagenet' and the fully connected layers excluded (`include_top=False`). The input shape and pooling type are specified as `img_shape` and 'avg' respectively.

Next, the code freezes the weights of all layers in the pre-trained model by setting their `trainable` attribute to `False`. This ensures that the pre-trained weights are not updated during training.

Custom layers are then added on top of the pre-trained model. Batch normalization is applied to normalize the activations, followed by a fully connected layer with 1024 units and ReLU activation. Dropout with a rate of 0.2 is used to reduce overfitting. The final dense layer with `num_classes` units and softmax activation serves as the output layer for classification.

The model is created by specifying the inputs as the input of the pre-trained model and the outputs as the predictions from the custom layers. The model is compiled using the Adam optimizer with a learning rate of 0.001, 'categorical_crossentropy' as the loss function for multi-class classification, and 'accuracy' as the metric for evaluation.

Finally, the model summary is displayed, showing the architecture of the model, the output shapes of each layer, and the number of parameters in each layer.
"""

# Load pre-trained VGG16
pre_trained =  InceptionV3(weights='imagenet', include_top=False, input_shape=img_shape, pooling='avg')

for layer in pre_trained.layers:
    layer.trainable = False
x = pre_trained.output
x = BatchNormalization()(x)
x = Dense(1024, activation='relu')(x)
x = Dropout(0.2)(x)
predictions = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=pre_trained.input, outputs=predictions)
model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

"""### Model fitting

train the model using `fit_generator` with training and validation data generators. It calculate the steps per epoch and validation steps, then train the model for 25 epochs, displaying progress and metrics. The training history is stored in the `history` variable.
"""

history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=25
)

"""## plotting the graph

This code plots the training and validation loss and accuracy over the epochs. The loss and accuracy values from the `history` object are used to create line plots. The x-axis represents the epoch number, while the y-axis represents the loss or accuracy. Separate plots are created for training and validation data, and legends are added to differentiate them.
"""

plt.xlabel('Epoch Number')
plt.ylabel('Loss')
plt.plot(history.history['loss'], label='training set')
plt.plot(history.history['val_loss'], label='test set')
plt.legend()

plt.xlabel('Epoch Number')
plt.ylabel('Accuracy')
plt.plot(history.history['accuracy'], label='training set')
plt.plot(history.history['val_accuracy'], label='test set')
plt.legend()

"""### saving the model"""

model_name = 'weather_image_recognition(inceptionV3).h5'
model.save(model_name, save_format='h5')

class_map = train_data.class_indices
classes = []
for key in class_map.keys():
    classes.append(key)

"""### image label and prediction and visualization"""

def predict_image(filename, model):
    img_ = image.load_img(filename, target_size=(228, 228))
    img_array = image.img_to_array(img_)
    img_processed = np.expand_dims(img_array, axis=0)
    img_processed /= 255.

    prediction = model.predict(img_processed)

    index = np.argmax(prediction)

    plt.title("Prediction - {}".format(str(classes[index]).title()), size=18, color='green')
    plt.imshow(img_array)

predict_image('dataset/sandstorm/2938.jpg', model)

predict_image('dataset/rain/136.jpg', model)

predict_image('/kaggle/input/weather-dataset/dataset/rain/1038.jpg', model)

predict_image('/kaggle/input/weather-dataset/dataset/sandstorm/2933.jpg', model)

predict_image('/kaggle/input/weather-dataset/dataset/rainbow/0613.jpg', model)

"""### importing libraries for classification report , accuracy score and confusion matrix"""

from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Load the saved model
model = tf.keras.models.load_model('weather_image_recognition(inceptionV3).h5')

# Evaluate the model on the original validation data
val_images, val_labels = next(iter(val_data))
val_predictions = model.predict(val_images)
val_pred_labels = np.argmax(val_predictions, axis=1)
val_true_labels = np.argmax(val_labels, axis=1)

"""### f1 score"""

# Classification Report
print('Classification Report:')
print(classification_report(val_true_labels, val_pred_labels, zero_division=1))

"""### accuracy score"""

# Accuracy Score
accuracy = accuracy_score(val_true_labels, val_pred_labels)
print('Accuracy Score:', accuracy)

"""### confusion matrix"""

# Confusion Matrix
cm = confusion_matrix(val_true_labels, val_pred_labels)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, cmap='Greens', fmt='g', cbar=False)
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.title('Confusion Matrix')
plt.show()

