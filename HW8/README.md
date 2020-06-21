# Part 1: Image Annotation

* In the time allowed, how many images did you annotate?  

Annotated 73 images in 25 minutes,

* Home many instances of the Millennium Falcon did you annotate? How many TIE Fighters?

47 Millennium Falcons

50 Tie Fighters

* Based on this experience, how would you handle the annotation of large image data set?
Think about image augmentation? How would augmentations such as flip, rotation, scale, cropping, and translation effect the annotations?

Image argumentation helps the model not to overfit to the dataset.

# Part 2: Image Augmentation

## Describe the following augmentations in your own words

* Flip

Images can be flipped horizontally and vertically. This can double the number of images. In some cases horizontal flips does not make sense (image of a building)

* Rotation

The image can be rotated by a certain degree to create a new agrumented picture. Image dimensions may not be preserved after rotation. Adds 2-4 times the number of images. 

* Scale

Scaling can be thought of as zooming in and out. It forces some assumptions about what is outside of what we see.

* Crop

Sample a section from the original image, then resize this section to the origonal image dimensions. 

* Translation

Translation  is moving an object along the X and or Y directions

* Noise

This is adding some form of noise to the data improves the robustness of the network. 

# Part 3: Audio Annotation

* Image annotations require the coordinates of the objects and their classes; in your option, what is needed for an audio annotation?

For audio it is the time from the beginning of the clip

