# Copyright 2021 The TensorFlow Hub Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# Copyright 2023 antillia.com Toshiyuki Arai

# 2023/11/30 to-arai

# TensorflowMoveNetHumanPoseEstimator.py
#
# This Python code is based on the followingtf-tutorial
# https://github.com/tensorflow/docs/blob/master/site/en/hub/tutorials/movenet.ipynb

import os
import sys
import shutil
import sys
import time
import pprint
import glob
import cv2
import numpy as np
import traceback

import tensorflow as tf
import tensorflow_hub as hub

from ConfigParser import ConfigParser

from HumanPoseVisualizer import HumanPoseVisualizer


class TensorflowMoveNetHumanPoseEstimator:

  def __init__(self, inference_conf):
    print("=== TensorflowMoveNetHumanPoseEstimator")
    config    = ConfigParser(inference_conf)
    INFERENCE = "inference"
    self.images_dir  = config.get(INFERENCE, "images_dir")
    self.outputs_dir = config.get(INFERENCE, "outputs_dir")
    if not os.path.exists(self.images_dir):
        raise Exception("Not found " + self.images_dir)
    if os.path.exists(self.outputs_dir):
        shutil.rmtree(self.outputs_dir)
    if not os.path.exists(self.outputs_dir):
        os.makedirs(self.outputs_dir)
    
    #
    model_name = config.get(INFERENCE, "model_name", dvalue="movenet_thunder")
    
    if "movenet_lightning" in model_name:
      self.module = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
      self.input_size = 192
    elif "movenet_thunder" in model_name:
      self.module = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/4")
      self.input_size = 256
    else:
      raise ValueError("Unsupported model name: %s" % model_name)

      
    self.model = self.module.signatures['serving_default']

    self.visualizer = HumanPoseVisualizer(config_file)
    
 
  def infer(self):
    image_files  = glob.glob(self.images_dir + "/*.jpg")
    image_files += glob.glob(self.images_dir + "/*.png")
    
    for image_file in image_files:
      print("--- image_file {}".format(image_file))
      image = tf.io.read_file(image_file)
      image = tf.image.decode_jpeg(image, channels=3, dct_method="INTEGER_ACCURATE")
      basename = os.path.basename(image_file)

      # Resize and pad the image to keep the aspect ratio and fit the expected size.
      input_image = tf.expand_dims(image, axis=0)
      input_image = tf.image.resize_with_pad(input_image, self.input_size, self.input_size)

      # Run model inference.
      # SavedModel format expects tensor type of int32.
      input_image = tf.cast(input_image, dtype=tf.int32)
      
      outputs = self.model(input_image)
      # Output is a [1, 1, 17, 3] tensor.
      keypoints_with_scores = outputs['output_0'].numpy()
      
      # Visualize the predictions with image.
      display_image = tf.expand_dims(image, axis=0)
      #display_image = tf.cast(tf.image.resize_with_pad(display_image, 1280, 1280), dtype=tf.int32)
      output_overlay = self.visualizer.draw_prediction_on_image(
         np.squeeze(display_image.numpy(), axis=0), keypoints_with_scores)
      output_image_file = os.path.join(self.outputs_dir, basename)
      output_overlay = cv2.cvtColor(output_overlay, cv2.COLOR_BGR2RGB)

      cv2.imwrite(output_image_file, output_overlay)
      print("--- saved {}".format(output_image_file))
    

if __name__ == "__main__":
  try:
    config_file = "./inference.conf"
    if len(sys.argv) ==2:
      config_file = sys.argv[1]

    estimator = TensorflowMoveNetHumanPoseEstimator(config_file)
    estimator.infer()

  except:
    traceback.print_exc()
