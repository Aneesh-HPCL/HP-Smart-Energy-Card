# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 14:55:51 2026

@author: 32003200
"""

import streamlit as st
import cv2
import numpy as np
import tempfile

# Title and instructions
st.title("🔥 Burner Health Check")

st.write("Upload a flame image to analyze burner health.")

st.info(""" **Recommended settings:** 
        \n -Capture flame image in good lighting
        \n -Avoid background clutter
        \n -Ensure clear focus""")

# File uploader
uploaded_file = st.file_uploader("Upload Flame Image", type=["jpg", "jpeg", "png"])

def analyze_flame(image_path):
    """Simple flame health analysis based on color and brightness."""
    img = cv2.imread(image_path)
    if img is None:
        return "Invalid image uploaded."

    img = cv2.imread(image_path)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    def adaptive_gamma(image):
    
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
        mean_intensity = np.mean(gray)
    
        gamma = np.log(0.5*255) / np.log(mean_intensity + 1)
    
        gamma = max(0.5, min(gamma, 2.0))
    
        lookup_table = np.array(
            [((i / 255.0) ** gamma) * 255
             for i in np.arange(0,256)]
        ).astype("uint8")
    
        corrected = cv2.LUT(image, lookup_table)
    
        return corrected
    
    gamma = adaptive_gamma(img)
    
    blur = cv2.GaussianBlur(gamma,(5,5),0)
    
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21,
        5
    )
    
    kernel = np.ones((3,3),np.uint8)
    
    open = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        kernel
    )
    
    mask = cv2.morphologyEx(
        open,
        cv2.MORPH_CLOSE,
        kernel
    )
    
    blue_lower = np.array([90,50,50])
    
    blue_upper = np.array([140,255,255])
    
    blue_mask = cv2.inRange(
        hsv,
        blue_lower,
        blue_upper
    )
    
    yellow_lower = np.array([10,50,50])
    
    yellow_upper = np.array([40,255,255])
    
    yellow_mask = cv2.inRange(
        hsv,
        yellow_lower,
        yellow_upper
    )
    
    flame_pixels = np.sum(mask > 0)
    
    blue_pixels = np.sum(blue_mask > 0)
    
    yellow_pixels = np.sum(yellow_mask > 0)
    
    blue_percentage = (
        blue_pixels / max(flame_pixels,1)
    ) * 100
    
    yellow_percentage = (
        yellow_pixels / max(flame_pixels,1)
    ) * 100
    
    blue_score = min(blue_percentage,100)
    
    yellow_penalty = min(yellow_percentage,100)
    
    color_score = (
        0.7*blue_score +
        0.3*(100-yellow_penalty)
    )
    
    color_score = np.clip(
        color_score,
        0,
        100
    )
    
    # FINAL BURNER HEALTH INDEX
    
    ref_color_score=58.70743221452799 # for healthy burner
    
    burner_health_index = abs(ref_color_score-color_score)

    # Simple rule: if flame coverage is too low, burner may be unhealthy
    if burner_health_index < 5:
        return "✅ Burner is healthy."
    else:
        return "⚠️ Burner needs replacement."

# Process uploaded image
if uploaded_file is not None:
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Run analysis
    result = analyze_flame(tmp_path)
    st.subheader("Analysis Result")
    st.success(result if "healthy" in result else result)
