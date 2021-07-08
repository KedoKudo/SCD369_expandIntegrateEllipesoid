# import mantid algorithms, numpy and matplotlib
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np

import os
directory = os.path.dirname(os.path.realpath(__file__))

Load(Filename='/SNS/TOPAZ/IPTS-23996/nexus/TOPAZ_36079.nxs.h5',
     OutputWorkspace='TOPAZ_36079.nxs_event',
     FilterByTofMin=500,
     FilterByTofMax=16666)

FilterBadPulses(InputWorkspace='TOPAZ_36079.nxs_event',
                OutputWorkspace='TOPAZ_36079.nxs_event',
                LowerCutoff=25)

LoadIsawDetCal(InputWorkspace='TOPAZ_36079.nxs_event',
               Filename='/SNS/TOPAZ/IPTS-23996/shared/calibration/TOPAZ_2020A.DetCal')

ConvertToMD(InputWorkspace='TOPAZ_36079.nxs_event',
            QDimensions='Q3D',
            dEAnalysisMode='Elastic',
            Q3DFrames='Q_sample',
            LorentzCorrection=True,
            OutputWorkspace='TOPAZ_36079.nxs_md',
            MinValues='-12,-12,-12',
            MaxValues='12,12,12',
            SplitInto='2',
            SplitThreshold=50,
            MaxRecursionDepth=13,
            MinRecursionDepth=7)

FindPeaksMD(InputWorkspace='TOPAZ_36079.nxs_md',
            PeakDistanceThreshold=0.12025531914893617,
            MaxPeaks=1200,
            DensityThresholdFactor=100,
            EdgePixels=19,
            OutputWorkspace='TOPAZ_36079.nxs_peaks')

FindUBUsingFFT(PeaksWorkspace='TOPAZ_36079.nxs_peaks', MinD=3, MaxD=7, Tolerance=0.12)
IndexPeaks(PeaksWorkspace='TOPAZ_36079.nxs_peaks', Tolerance=0.12, RoundHKLs=False)

SelectCellOfType(PeaksWorkspace='TOPAZ_36079.nxs_peaks',
                 CellType='Hexagonal',
                 Apply=True, TransformationMatrix='0,1,0,0,0,1,1,0,0')

OptimizeLatticeForCellType(PeaksWorkspace='TOPAZ_36079.nxs_peaks',
                          CellType='Hexagonal',
                          Apply=True, Tolerance=0.06,
                          EdgePixels=19, OutputDirectory=directory)

IndexPeaks(PeaksWorkspace='TOPAZ_36079.nxs_peaks',
           Tolerance=0.06,
           ToleranceForSatellite=0.05,
           RoundHKLs=False,
           ModVector1='0.125,0,0',
           ModVector2='0,0.125,0',
           ModVector3='-0.125,0.125,0',
           MaxOrder=1,
           CrossTerms=False,
           SaveModulationInfo=True)

IntegrateEllipsoids(InputWorkspace='TOPAZ_36079.nxs_event',
                    PeaksWorkspace='TOPAZ_36079.nxs_peaks',
                    RegionRadius=0.11,
                    SpecifySize=True,
                    PeakSize=0.085,
                    BackgroundInnerSize=0.086,
                    BackgroundOuterSize=0.11,
                    OutputWorkspace='TOPAZ_36079.nxs_peaks',
                    CutoffIsigI=5,
                    UseOnePercentBackgroundCorrection=False,
                    SatelliteRegionRadius=0.1,
                    SatellitePeakSize=0.08,
                    SatelliteBackgroundInnerSize=0.081,
                    SatelliteBackgroundOuterSize=0.1)
