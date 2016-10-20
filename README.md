# randoPythonScripts
This is a repository where some potentially useful python scripts are stored.  A brief description of each is given below.

*crop_image.py:*    applies a mask to an image.

*niiToPngConverter.py:*    converts a file of type .nii.gz to a .png

*convertTrakEMToRenderData.py:*    takes an TrakEM rigid_align.xml file and turns it into a JSON file that's readable by Render.  Note that there's an error in the mask file given, and that you should figure out how to implement your own masking image.

*ArtToTrakEMTransformationComparer.py and trakEMDistortionFieldScript.bsh*    A non-linear model was used to generate the distortion field given by the .svg file (known as "Art's file").  Another non-linear model's generation is compare to the .svg file.  We wanted to see if the two models were giving the same results.  A .svg file is generated for the differences between the two plots.  The secondary file was produced using ImageJ, TrakEM2, and beanshell, the code of which can be found in the file trakEMDistortionFieldScript.bsh in this repo.

