# randoPythonScripts
This is a repository where some potentially useful python scripts are stored.  A brief description of each is given below.

*crop_image.py:*    applies a mask to an image.

*niiToPngConverter.py:*    converts a file of type .nii.gz to a .png

*convertTrakEMToRenderData.py:*    takes an TrakEM rigid_align.xml file and turns it into a JSON file that's readable by Render.  Note that there's an error in the mask file given, and that you should figure out how to implement your own masking image.

*ArtToTrakEMTransformationComparer.py and trakEMDistortionFieldScript.bsh*    A non-linear model was used to generate the distortion field given by the .svg file (known as "Art's file").  Another non-linear model's generation is compare to the .svg file.  We wanted to see if the two models were giving the same results.  A .svg file is generated for the differences between the two plots.  The secondary file was produced using ImageJ, TrakEM2, and beanshell, the code of which can be found in the file trakEMDistortionFieldScript.bsh in this repo.

*mapPseudoTilesToRealTiles.py* Two transformations are used by TrakEM to align individual Transmission Electron Microscope Camera Array (TEMCA) micrographs, "real tiles", with one another.  The first transformation is nonlinear, distorting the micrograph's edges so that it aligns with its neighboring micrographs.  The second transformation is affine, causing the concatenated micrographs to then roughly align with zLayers above and below it, so that the 3D slices make a continuous representation of the sectioned data.  From here, the micrographs were flattened into a single image, followed be an application of a mask, trimming the edges of the flattened micrograph.  This masked and trimmed image then has pseudo tile objects made from it in a grid-like fashion, which undergo further nonlinear transformation for 3D alignment.  The purpose of this script is to figure out, and record from the corresponding masks which pseudo tiles contain which raw-data real tiles within them for each zLayer in the data set.
