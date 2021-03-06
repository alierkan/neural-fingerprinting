"""
The model is adapted from the tensorflow tutorial:
https://www.tensorflow.org/get_started/mnist/pros
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D, BatchNormalization
from keras.layers import Activation
from keras.losses import categorical_crossentropy
from third_party.lid_adversarial_subspace_detection.util import (get_data, get_model, cross_entropy) #, get_noisy_samples)
import tensorflow as tf
from model import *
K.set_image_data_format('channels_first')

class Model(object):
  def __init__(self, torch_model=CW_Net,softmax=True):
    self.x_input = tf.placeholder(tf.float32, shape = [None, 784])
    self.y_input = tf.placeholder(tf.int64, shape = [None])

    self.x_image = tf.reshape(self.x_input, [-1, 1, 28, 28])

    # Model from https://arxiv.org/pdf/1608.04644.pdf
    if(isinstance(torch_model,CW_Net)):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3),
                         activation='relu',
                         input_shape=(1, 28, 28),
                         name='conv1'))
        l1 = BatchNormalization(axis=1,name='bnm1',momentum=0.1)
        model.add(l1)
        model.add(Conv2D(32, (3, 3),activation='relu',name='conv2'))
        model.add(BatchNormalization(axis=1,name='bnm2',momentum=0.1))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (3, 3), activation='relu', name='conv3'))
        model.add(BatchNormalization(axis=1,name='bnm3',momentum=0.1))
        model.add(Conv2D(64, (3, 3), activation='relu', name='conv4'))
        model.add(BatchNormalization(axis=1,name='bnm4',momentum=0.1))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(200, activation='relu', name='fc1'))
        model.add(BatchNormalization(axis=1,name='bnm5',momentum=0.1))
        model.add(Dense(200, activation='relu', name='fc2'))
        model.add(BatchNormalization(axis=1,name='bnm6',momentum=0.1))
        model.add(Dense(10, activation=None, name='fc3'))

    # Uncomment for LeNet
    elif(isinstance(torch_model,LeNet)):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(5, 5),
                         activation='relu',
                         input_shape=(1,28,28),
                         name='conv1'))
        model.add(BatchNormalization(axis=1,name='bnm1',momentum=0.1))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (5, 5), activation='relu', name='conv2'))
        model.add(BatchNormalization(axis=1,name='bnm2',momentum=0.1))

        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(200, activation='relu', name='fc1'))
        model.add(BatchNormalization(axis=1,name='bnm3',momentum=0.1))
        model.add(Dense(84, activation='relu', name='fc2'))
        model.add(BatchNormalization(axis=1,name='bnm4',momentum=0.1))
        model.add(Dense(10, activation=None, name='fc3'))

    if(softmax==True):
        # Set softmax=False for CW-l2 attack
        model.add(Activation('softmax'))

    model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.Adadelta(),
                      metrics=['accuracy'])

    self.model = model

    self.logits = model(self.x_image)
    y_ = self.y_input
    y_conv=self.logits
    x=self.x_input
    y_xent = tf.nn.sparse_softmax_cross_entropy_with_logits(
    labels=self.y_input, logits=self.logits)

    self.xent = tf.reduce_sum(y_xent)
    self.y_pred = tf.argmax(self.logits, 1)
    correct_prediction = tf.equal(self.y_pred, self.y_input)
    self.num_correct = tf.reduce_sum(tf.cast(correct_prediction, tf.int64))
    self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

  @staticmethod


  def _conv2d(x, W):
      return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME')

  @staticmethod
  def _max_pool_2x2( x):
      return tf.nn.max_pool(x,
                            ksize = [1,2,2,1],
                            strides=[1,2,2,1],
                            padding='SAME')

  @staticmethod
  def _weight_variable(shape,name=None):
    """weight_variable generates a weigh  t        variable of a given shape."""
    initial = tf.truncated_normal(shape, stddev=0.01)+0.01
    return tf.Variable(initial,name=name)

  @staticmethod
  def _bias_variable1(shape,name=None):
    """bias_variable generates a bias variable of a given shape."""
    initial = tf.constant(0.5, shape=shape)
    return tf.Variable(initial,name=name)

  @staticmethod
  def _bias_variable(shape,name=None):
    """bias_variable generates a bias variable of a given shape."""
    initial = tf.constant(0.5, shape=shape)
    return tf.Variable(initial,name=name)


