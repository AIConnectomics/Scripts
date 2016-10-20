# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 11:30:45 2016

@author: ariaj
"""

import scipy.misc
import SimpleITK as itk

def itk_imread(fn):
    r = itk.ImageFileReader()
    r.SetFileName(fn)
    I = r.Execute()
    del r
    return itk.GetArrayFromImage(I)

cropbox_fn = "mask.nii.gz"
output = itk_imread(cropbox_fn)[0].astype('bool')
scipy.misc.imsave('outputmask.png', output)
