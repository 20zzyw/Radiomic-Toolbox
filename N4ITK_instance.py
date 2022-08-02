#!usr/bin/python

import os
import SimpleITK as sitk
import numpy as np 
import scipy.ndimage.interpolation
import skimage.exposure
import skimage.filters
import skimage.transform

path="//Users//zhangyuwei//Desktop//test"
ShrinkFactor = 4

for i in os.walk(path):    
    for j in range(len(i[2])):
        if os.path.splitext(i[2][j])[1] == ".gz" :
            print(os.path.splitext(i[2][j])[0])
            nifti_file = sitk.ReadImage(os.path.join(i[0],i[2][j]))
            mask_img   = sitk.BinaryThreshold(nifti_file, 80, 5000)

            mask_filename    = "globalmask_" + os.path.splitext(i[2][j])[0] + ".gz"
            output_filename  = "N4ITKcorrected_" + os.path.splitext(i[2][j])[0] + ".gz"
            output_biasname1 = "bias_in_" + os.path.splitext(i[2][j])[0] + ".gz"
            output_biasname2 = "bias_out_" + os.path.splitext(i[2][j])[0] + ".gz"
            sitk.WriteImage(mask_img, mask_filename)

            nifti_shape  = sitk.GetArrayFromImage(nifti_file)
            nifti_shape  = nifti_shape.shape
            
            # Call and initialize an N4 corrector instance.
            corrector                              = sitk.N4BiasFieldCorrectionImageFilter()
            corrector.SetMaximumNumberOfIterations = 50
            corrector.SetNumberOfHistogramBins     = 128
            corrector.SetSplineOrder               = 10
            corrector.SetConvergenceThreshold      = 0.001
            corrector.SetNumberOfControlPoints     = 8
            print("> Initializing Compelete!")

            if ShrinkFactor > 1 :
                
                shrinked_img  = sitk.Shrink(nifti_file, [ShrinkFactor] * nifti_file.GetDimension())
                shrinked_mask = sitk.Shrink(mask_img, [ShrinkFactor] * nifti_file.GetDimension())
                
                shrinked_img = sitk.Cast(shrinked_img, sitk.sitkFloat32)
                #shrinked_mask = sitk.Cast(shrinked_mask, sitk.sitkFloat32)

                print("> Starting Execution...")
                corrected_img = corrector.Execute(shrinked_img, shrinked_mask)
                print("> Execution Complete!")

                # Estimate the bias field of corrected image                              
                re_corrected = corrector.Execute(corrected_img, shrinked_mask)
                print("> Corrected Bias Estimation Complete!")

                corrected_img = sitk.GetArrayFromImage(corrected_img)
                corrected_img[corrected_img == 0] = 0.001
                re_corrected = sitk.GetArrayFromImage(re_corrected)
                re_corrected[re_corrected == 0] = 0.001
                shrinked_img = sitk.GetArrayFromImage(shrinked_img)
                
                # Generate biasfield
                shrinked_bias  = shrinked_img / corrected_img
                corrected_bias = corrected_img / re_corrected

                # Output
                output_bias  = scipy.ndimage.zoom(shrinked_bias, np.array(nifti_shape) / shrinked_bias.shape)
                output_bias2 = scipy.ndimage.zoom(corrected_bias, np.array(nifti_shape) / shrinked_bias.shape)
                output_img   = sitk.GetArrayFromImage(nifti_file) / output_bias

                output_bias  = sitk.GetImageFromArray(output_bias)
                output_bias2 = sitk.GetImageFromArray(output_bias2)
                output_img   = sitk.Cast(sitk.GetImageFromArray(output_img), sitk.sitkUInt16)
                
                sitk.WriteImage(output_img, output_filename)
                sitk.WriteImage(output_bias, output_biasname1)
                sitk.WriteImage(output_bias2, output_biasname2)
                print("> Save Complete!")
                
            else:
                source_img = sitk.Shrink(nifti_file, [ShrinkFactor] * nifti_file.GetDimension())
                mask_img   = sitk.Shrink(mask_img, [ShrinkFactor] * mask_img.GetDimension())
                source_img = sitk.Cast(source_img, sitk.sitkFloat32)

                output_img = corrector.Execute(source_img, mask_img)
                output_img = sitk.Cast(output_img, sitk.sitkUInt16)

                sitk.WriteImage(output_img, output_filename)
                #biasfield_img = source_img / output_img
                #biasfield_img[biasfield_img <  0.5] = 0.5