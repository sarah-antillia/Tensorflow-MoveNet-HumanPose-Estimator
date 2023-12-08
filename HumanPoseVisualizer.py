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
# 2023/12/10 to-arai :Modified not to use matplot.lib

# This code has been taken from the following tutorial
#https://github.com/tensorflow/docs/blob/master/site/en/hub/tutorials/movenet.ipynb

#@title Helper functions for visualization

# Some methods in HumanPoseVisualizer class have been taken from

# https://www.kaggle.com/code/ibrahimserouis99/human-pose-estimation-with-movenet

# See also
# https://github.com/Kazuhito00/MoveNet-Python-Example/tree/main
# https://github.com/geaxgx/openvino_movenet_multipose/tree/main

import cv2
import numpy as np

# Some modules to display an animation using imageio.
import imageio
from ConfigParser import ConfigParser
INFERENCE = "inference"
VISUALIZE = "visualize"

# Dictionary that maps from joint names to keypoint indices.
KEYPOINT_DICT = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16
}

cyan    = (255, 255, 0)
magenta = (255, 0, 255)

EDGE_COLORS = {
    (0, 1): magenta,
    (0, 2): cyan,
    (1, 3): magenta,
    (2, 4): cyan,
    (0, 5): magenta,
    (0, 6): cyan,
    (5, 7): magenta,
    (7, 9): cyan,
    (6, 8): magenta,
    (8, 10): cyan,
    (5, 6): magenta,
    (5, 11): cyan,
    (6, 12): magenta,
    (11, 12): cyan,
    (11, 13): magenta,
    (13, 15): cyan,
    (12, 14): magenta,
    (14, 16): cyan
}

class HumanPoseVisualizer:
  def __init__(self, config_file):
    self.config = ConfigParser(config_file)
    self.threshold = self.config.get(INFERENCE, "threshold", dvalue=0.1)
    
    self.line_thickness= self.config.get(VISUALIZE, "line_thickness" , dvalue=2)
    self.circle_radius = self.config.get(VISUALIZE, "circle_radius" , dvalue=6)
    self.circle_color  = self.config.get(VISUALIZE, "circle_color" , dvalue=(255, 0, 0))


  def save(self, image, keypoints_with_scores, crop_region=None, close_figure=False,
      output_image_height=None):
      
    self.draw_prediction_on_image(
      image, keypoints_with_scores, crop_region=None, close_figure=False,
      output_image_height=None)
      
                         
  def draw_keypoints(self, image, keypoints):
    """Draws the keypoints on an image"""
    #print("=== draw_keypoints ")
    h, w, c = image.shape
    
    keypoints_coordinates = np.squeeze(np.multiply(keypoints, [h, w,1]))
    #Iterate through the points
    for keypoint in keypoints_coordinates:
        # Unpack the keypoint values : y, x, confidence score
        keypoint_y, keypoint_x, keypoint_confidence = keypoint
        if keypoint_confidence > self.threshold:
            """"
            Draw the circle
            Note : A thickness of -1 px will fill the circle shape by the specified color.
            """
            cv2.circle(
                img=image, 
                center=(int(keypoint_x), int(keypoint_y)), 
                radius=self.circle_radius, 
                color=self.circle_color, 
                thickness=-1
            )
    return keypoints_coordinates


  def draw_edges(self, keypoints_coordinates, image, edges_colors):
    """
    Draws the edges on an image by using keypoints_coordinates.
    """
    
    # Iterate through the edges 
    for edge, color in edges_colors.items():
        # Get the dict value associated to the actual edge
        p1, p2 = edge
        # Get the points
        y1, x1, confidence_1 = keypoints_coordinates[p1]
        y2, x2, confidence_2 = keypoints_coordinates[p2]
        # Draw the line from point 1 to point 2, the confidence > threshold
        if (confidence_1 > self.threshold) & (confidence_2 > self.threshold):      
            cv2.line(
                img=image, 
                pt1=(int(x1), int(y1)),
                pt2=(int(x2), int(y2)), 
                color=color, 
                thickness=self.line_thickness, 
                lineType=cv2.LINE_AA # Gives anti-aliased (smoothed) line which looks great for curves
            )
    return image
     
     
  def draw_prediction_on_image(self, image, keypoints_with_scores):
    print("=== draw_prediction_on_image")
    for keypoints_with_score in keypoints_with_scores:
      keypoints_coordinates  = self.draw_keypoints(image, keypoints_with_score)

      self.draw_edges(keypoints_coordinates, image, EDGE_COLORS)
    return image     
    

  #def to_gif(self, images, duration):
  #  """Converts image sequence (4D numpy array) to gif."""
  #  imageio.mimsave('./animation.gif', images, duration=duration)
  #  return embed.embed_file('./animation.gif')
