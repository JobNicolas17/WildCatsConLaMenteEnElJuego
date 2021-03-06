from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras.preprocessing import image
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.optimizers import SGD

import cv2
import pandas as pd
import numpy as np
from keras.preprocessing.image import ImageDataGenerator

import tensorflow as tf

import os
os.environ['CUDA_VISIBLE_DEVICES'] = "1"

from keras import backend as K

sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))

K.tensorflow_backend._get_available_gpus()

##
#Se establecen los paths
path_csv = '/media/user_home2/vision2020_01/Data/iWildCam2019/train.csv'
path_train = '/media/user_home2/vision2020_01/Data/iWildCam2019/train_images'

##
#Se crea el modelo

# create the base pre-trained model
base_model = InceptionResNetV2(weights='imagenet', include_top=False)

# add a global spatial average pooling layer
x = base_model.output
x = GlobalAveragePooling2D()(x)
# let's add a fully-connected layer
x = Dense(1024, activation='relu')(x)
# and a logistic layer -- let's say we have 200 classes
predictions = Dense(14, activation='softmax')(x)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)

# first: train only the top layers (which were randomly initialized)
# i.e. freeze all convolutional InceptionV3 layers
# for layer in base_model.layers:
#     layer.trainable = False

# compile the model (should be done *after* setting layers to non-trainable)
# model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

##
#Se cargan los datos
train_df = pd.read_csv(path_csv)
train_df['category_id'] = train_df['category_id'].astype(str)

batch_size=32
img_size = 299
nb_epochs = 10

train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.25)
train_generator = train_datagen.flow_from_dataframe(
        dataframe = train_df,
        directory = path_train,
        x_col = 'file_name', y_col = 'category_id',
        target_size=(img_size,img_size),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training')

validation_generator  = train_datagen.flow_from_dataframe(
        dataframe = train_df,
        directory = path_train,
        x_col = 'file_name', y_col = 'category_id',
        target_size=(img_size,img_size),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation')

set(train_generator.class_indices)
nb_classes = 14
print(train_generator.class_indices)

##Se entrena el modelo usando fine-tune

# train the model on the new data for a few epochs
#model.fit(...)

# Train model
# history = model.fit_generator(
#             train_generator,
# #             steps_per_epoch = train_generator.samples // batch_size,
#             steps_per_epoch = 100,
#             validation_data = validation_generator,
# #             validation_steps = validation_generator.samples // batch_size,
#             validation_steps = 50,
#             epochs = nb_epochs,
#             verbose=2)

# at this point, the top layers are well trained and we can start fine-tuning
# convolutional layers from inception V3. We will freeze the bottom N layers
# and train the remaining top layers.

# let's visualize layer names and layer indices to see how many layers
# we should freeze:
#for i, layer in enumerate(base_model.layers):
#   print(i, layer.name)

# we chose to train the top 2 inception blocks, i.e. we will freeze
# the first 249 layers and unfreeze the rest:
# for layer in model.layers[:249]:
#    layer.trainable = False
# for layer in model.layers[249:]:
#    layer.trainable = True


##
#Metrica final
def f1(y_true, y_pred):
    def recall(y_true, y_pred):
        """Recall metric.

        Only computes a batch-wise average of recall.

        Computes the recall, a metric for multi-label classification of
        how many relevant items are selected.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(y_true, y_pred):
        """Precision metric.

        Only computes a batch-wise average of precision.

        Computes the precision, a metric for multi-label classification of
        how many selected items are relevant.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision
    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

##
# we need to recompile the model for these modifications to take effect
# we use SGD with a low learning rate
from keras.optimizers import SGD
from keras.callbacks import ReduceLROnPlateau

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2,
                              patience=5, min_lr=0.001)
model.compile(optimizer=SGD(lr=0.01, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy',f1])

# we train our model again (this time fine-tuning the top 2 inception blocks
# alongside the top Dense layers
#model.fit(...)

##
#Se establecen pesos para cada clase
#{'0': 0, '1': 1, '10': 2, '11': 3, '13': 4, '14': 5, '16': 6, '17': 7, '18': 8, '19': 9, '22': 10, '3': 11, '4': 12, '8': 13}

#Pesos alreves
# class_weight = {0: 1.,1: 22.,
#                 11: 39.,12: 59.,13: 19.,2: 120.,3: 18.,4: 15.,5: 97.,6: 22.,7: 28.,8: 43.,9: 9.,10: 3983.}
#Pesos son numero de instancias
# class_weight = {0: 131454.,1: 6102.,11: 3398.,12: 2210.,13: 6938.,2: 1093.,3: 7209.,4: 8623.,5: 1361.,6: 5975.,7: 4759.,
#                 8: 3035.,9: 14106.,10: 33.}
# class_weight = {0: 100.,1: 2.,11: 2.,12: 2.,13: 2.,2: 2.,3: 2.,4: 2.,5: 2.,6: 2.,7: 2.,
#                 8: 2.,9: 2.,10: 1.}
class_weight = {0: 1.,1: 50.,11: 50.,12: 50.,13: 50.,2: 50.,3: 50.,4: 50.,5: 50.,6: 50.,7: 50.,
                8: 50.,9: 50.,10: 100.}


##
#Se entrena
# Train model
history = model.fit_generator(
            train_generator,
#             steps_per_epoch = train_generator.samples // batch_size,
            steps_per_epoch = 100,
            validation_data = validation_generator,
#             validation_steps = validation_generator.samples // batch_size,
            validation_steps = 50,
            epochs = nb_epochs,
            verbose=2,
            class_weight=class_weight,
            callbacks=[reduce_lr])