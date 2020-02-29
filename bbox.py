# import time
import json
import boto3
import logging
# import sys
# import os
import ntpath
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import math

IMAGE_PATH = "/home/ec2-user/proj/rekog/images/all/"
# OUT_PATH = "/home/ec2-user/proj/rekog/output.jpg"
OUT_PATH = "/home/ec2-user/output.jpg"
BUCKET = "mbuyisabuck"
rekog = boto3.client('rekognition')
# src_im_path = IMAGE_PATH+"Joseph_Kabila_0001.jpg"



def im2bytes(src, REVERSE=False):
	if not REVERSE: # convert image to bytes
		imgByteArr = BytesIO()
		src.save(imgByteArr, format="JPEG")
		imgByteArr = imgByteArr.getvalue()
		return imgByteArr
	else: # convert image bytes to image
		pass
	
def draw_bbox1(x0, y0, x1, y1, src_im):
	""" 
	Description: Draw a bounding box given coordinates > [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]
	Inputs: top left x_coord, top left y_coord, bottom right x_coord, bottom right y_coord, PIL image
	Output: Bounded PIL image	 
	"""
	
	out_im = ImageDraw.Draw(src_im)
	out_im.rectangle((x0, y0, x1, y1), fill=None, outline=(255,255,255) )
	del out_im
	return src_im

def draw_bbox2(bbox, src_im):
	""" 
	Description: Draw a bounding box given Rekognition-style coordinates 
	Inputs: top left x_coord, top left y_coord, bottom right x_coord, bottom right y_coord, PIL image
	Output: Bounded PIL image	 
	"""
	
	(w,h) = image_info(src_im)
	x1,y1,x0,y0 = math.floor(bbox['Width']*w), math.floor(bbox['Height']*h), math.floor(bbox['Left']*w), math.floor(bbox['Top']*h)
	x1,y1 = x0+x1, y0+y1
	return draw_bbox1(x0, y0, x1, y1, src_im)

def image_info(im):
	print("Image size:", im.size)
	print("Image format:", im.format)
	print("Image mode:", im.mode)
	return im.size

def read_image(im_path):
	im = Image.open(im_path)
	return im

def save_image(im, out_path=OUT_PATH):
	im.save(OUT_PATH)

def upload_to_s3(im_path):
	# OUT_PATH
	s3 = boto3.client('s3')
	s3.upload_file(im_path, BUCKET, 'rekog/'+ntpath.basename(im_path) )

def detectFaces(im, option=None):	
	response = ''
	if option == 's3':
		response = rekog.detect_faces(
		    Image={
				'S3Object': {
					'Bucket': 'string',
					'Name': 'rekog/input/'+im
				}
			},
			Attributes=['ALL']
		)				
	else:
		imgByteArr = im2bytes(im) # convert to image to bytes
		response = rekog.detect_faces(
		    Image={
				'Bytes':  imgByteArr
			},
			Attributes=['ALL'] 
		)
	return response
	
	
def main():
	im_path = IMAGE_PATH + "Joseph_Kabila_0001.jpg"
	s3im = "faces.jpg"
	im = read_image(im_path)
	image_info(im)
	 
	# face_info = detectFaces(im)
	face_info = detectFaces(s3im,'s3')
	
	b_img = draw_bbox2(face_info['FaceDetails'][0]['BoundingBox'],im); 
	# save_image(b_img)
	# print(face_info)
	# return OUT_PATH 

main()

# scp -i nvirginia.pem ec2-user@18.209.140.236:/home/ec2-user/output.jpg /drives/c/Users/kchikama/Desktop/temp/rekognition/
