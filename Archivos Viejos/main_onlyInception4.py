'''
Copyright 2017 TensorFlow Authors and Kent Sommer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from keras import backend as K
import inception_v4
import numpy as np
import cv2


# If you want to use a GPU set its index here
#os.environ['CUDA_VISIBLE_DEVICES'] = ''


# This function comes from Google's ImageNet Preprocessing Script
def central_crop(image, central_fraction):
	"""Crop the central region of the image.
	Remove the outer parts of an image but retain the central region of the image
	along each dimension. If we specify central_fraction = 0.5, this function
	returns the region marked with "X" in the below diagram.
	   --------
	  |        |
	  |  XXXX  |
	  |  XXXX  |
	  |        |   where "X" is the central 50% of the image.
	   --------
	Args:
	image: 3-D array of shape [height, width, depth]
	central_fraction: float (0, 1], fraction of size to crop
	Raises:
	ValueError: if central_crop_fraction is not within (0, 1].
	Returns:
	3-D array
	"""
	if central_fraction <= 0.0 or central_fraction > 1.0:
		raise ValueError('central_fraction must be within (0, 1]')
	if central_fraction == 1.0:
		return image

	img_shape = image.shape
	depth = img_shape[2]
	fraction_offset = int(1 / ((1 - central_fraction) / 2.0))
	bbox_h_start = int(np.divide(img_shape[0], fraction_offset))
	bbox_w_start = int(np.divide(img_shape[1], fraction_offset))

	bbox_h_size = int(img_shape[0] - bbox_h_start * 2)
	bbox_w_size = int(img_shape[1] - bbox_w_start * 2)

	image = image[bbox_h_start:bbox_h_start+bbox_h_size, bbox_w_start:bbox_w_start+bbox_w_size]
	return image


def get_processed_image(img_path):
	# Load image and convert from BGR to RGB
	im = np.asarray(img_path)[:,:,::-1] #(cv2.imread(img_path))[:,:,::-1]
	im = central_crop(im, 0.875)
	im = cv2.resize(im, (299, 299))
	im = inception_v4.preprocess_input(im)
	if K.image_data_format() == "channels_first":
		im = np.transpose(im, (2,0,1))
		im = im.reshape(-1,3,299,299)
	else:
		im = im.reshape(-1,299,299,3)
	return im


if __name__ == "__main__":
	# Create model and load pre-trained weights
	model = inception_v4.create_model(weights='imagenet', include_top=True)
    #model

	#clasDia = diaONoche()
    # subset = sacarPaths(
	#	'/media/user_home2/vision2020_01/Data/iWildCam2019/iwildcam-2019-fgvc6/train.csv',
	#	'/media/user_home2/vision2020_01/Data/iWildCam2019/iwildcam-2019-fgvc6/train_images/')
	#preds_final = np.empty([len(subset[1]),1])
	#cont = 0
    #
	# for i in subset[1]:
	#     #Sacar Subset
	# 	#subset = sacarPaths('/Users/johngonzalez/Desktop/Trabajos JF/Documents/U/Octavo Semestre/Vision Artificial/Proyecto/iwildcam-2019-fgvc6/train.csv',
	# 	#					'/Users/johngonzalez/Desktop/Trabajos JF/Documents/U/Octavo Semestre/Vision Artificial/Proyecto/iwildcam-2019-fgvc6/train_images/')
    #
	# 	path_carpet = '/media/user_home2/vision2020_01/Data/iWildCam2019/iwildcam-2019-fgvc6/train_images/'
	# 	path_completo = path_carpet+i
	# 	#Day 'N' Night
	# 	hora = probarDia(path_completo,clasDia)
    #
	# 	# Open Class labels dictionary. (human readable label given ID)
	# 	#classes = eval(open('validation_utils/class_names.txt', 'r').read())
	# 	classes = [0,1,3,4,8,10,11,13,14,16,17,18,19,22]
    #
	# 	img_or = cv2.imread(path_completo)
	# 	#Preprocesamiento
	# 	if hora == 0: #De dia
	# 		im_efec = miWB_LB(img_or)
	# 	else:
	# 		im_efec = imclahe(img_or)
    #
	# 	# Load test image!
    #
	# 	img = get_processed_image(im_efec)
    #
	# 	# Run prediction on test image
	# 	preds = model.predict(img)
	# 	print("Class is: " + str(classes[np.argmax(preds)-1]))
	# 	print("Certainty is: " + str(preds[0][np.argmax(preds)]))
    #
	# 	preds_final[cont] = classes[np.argmax(preds)-1]
	# 	cont += 1
    #
	# f1_fin = f1_score(subset[3],preds_final,average='macro')