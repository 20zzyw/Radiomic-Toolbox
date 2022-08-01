#!/usr/bin/env python3
'''
    An optimal parameter instance for T2weighted cervical ca.

    N4 Parameters
    -Bspline grid resolution 10,10,10
    -Spline distance 100
    -Bias field Full Width at Half Maximum 0

    Advanced N4 Parameters
    -Number of iterations 300,200,100
    -Convergence threshold 0.0001
    -Bspline order 3(default)
    -Shrink factor 4(default)
    -Weight Image None
    -Wiener filter noise 0.00
    -Number of histogram bins 20
'''

from __future__ import print_function

import SimpleITK as sitk
import sys
import os

if len ( sys.argv ) < 2:
    print( "Usage: N4BiasFieldCorrection inputImage " + \
        "outputImage [shrinkFactor] [maskImage] [numberOfIterations] " +\
        "[numberOfFittingLevels]" )
    sys.exit ( 1 )


inputImage = sitk.ReadImage( sys.argv[1] )
print("N4BiasFieldCorrection: 1. ReadImage Finished.")

if len ( sys.argv ) > 4:
    maskImage = sitk.ReadImage( sys.argv[4] )
else:
    maskImage = sitk.OtsuThreshold( inputImage, 0, 1, 200 )
print("N4BiasFieldCorrection: 2. MaskImage Finished.")

if len ( sys.argv ) > 3:
    inputImage = sitk.Shrink( inputImage, [ int(sys.argv[3]) ] * inputImage.GetDimension() )
    maskImage = sitk.Shrink( maskImage, [ int(sys.argv[3]) ] * inputImage.GetDimension() )
print("N4BiasFieldCorrection: 3. Shrinkage Finished.")

inputImage = sitk.Cast( inputImage, sitk.sitkFloat32 )
print("N4BiasFieldCorrection: 4. Cast Finished.")

corrector = sitk.N4BiasFieldCorrectionImageFilter()
print("N4BiasFieldCorrection: 5. CreatFilter Finished.")

numberFilltingLevels = 4

if len ( sys.argv ) > 6:
    numberFilltingLevels = int( sys.argv[6] )

if len ( sys.argv ) > 5:
    corrector.SetMaximumNumberOfIterations( [ int( sys.argv[5] ) ] *numberFilltingLevels  )
print("N4BiasFieldCorrection: 6. SetMaximumNumberOfIterations Finished.")


output = corrector.Execute( inputImage, maskImage )
print("N4BiasFieldCorrection: Bias Correction Finished.")

sitk.WriteImage( output, sys.argv[2] )
