#!/usr/bin/env python
'''

Crop a list of images from a single downsampled mask

Usage:  crop_image.py mymask.nii.gz img1.tif img2.tif....
'''
import os
import sys
import logging
import numpy
import scipy.misc
import SimpleITK


def itk_imread(fn):
    r = SimpleITK.ImageFileReader()
    r.SetFileName(fn)
    I = r.Execute()
    del r
    return SimpleITK.GetArrayFromImage(I)


def itk_imwrite(fn, arr):
    w = SimpleITK.ImageFileWriter()
    w.SetFileName(fn)
    w.Execute(SimpleITK.GetImageFromArray(arr))
    del w


def MinimalBoundedBox(img, mask):
    '''expects (hopes?) image and mask same dimensions'''
    unm = numpy.argwhere(mask)
    vtx_0 = unm.min(0)
    vtx_1 = unm.max(0) + 1
    return img[vtx_0[0]:vtx_1[0], vtx_0[1]:vtx_1[1]]


if __name__ == "__main__":
    cropbox_fn = "mask.nii.gz"#sys.argv[1]
    image = "mypic.png"#sys.argv[2:]

# mask each flat image
#for i, image in enumerate(images):
img = itk_imread(image)
    #if not i:
mask = itk_imread(cropbox_fn)[0].astype('bool')
resampled = scipy.misc.imresize(
                        mask, img.shape, interp='nearest').astype('bool')
imgfn = os.path.join(os.path.dirname(image), '{}_cropped{}'.format(
        os.path.splitext(
            os.path.basename(image))[0], os.path.splitext(image)[-1]))
itk_imwrite(imgfn, MinimalBoundedBox(img, resampled))
del img
