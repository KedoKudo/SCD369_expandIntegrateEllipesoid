# import mantid algorithms, numpy and matplotlib
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np
​
Load(Filename='/SNS/TOPAZ/IPTS-23996/nexus/TOPAZ_36079.nxs.h5', 
     OutputWorkspace='TOPAZ_36079.nxs_event',
     FilterByTofMin=500, 
     FilterByTofMax=16666)
​
FilterBadPulses(InputWorkspace='TOPAZ_36079.nxs_event', 
                OutputWorkspace='TOPAZ_36079.nxs_event', 
                LowerCutoff=25)
​
LoadIsawDetCal(InputWorkspace='TOPAZ_36079.nxs_event', 
               Filename='/SNS/TOPAZ/IPTS-23996/shared/calibration/TOPAZ_2020A.DetCal')
​
CropToComponent('TOPAZ_36079.nxs_event', ComponentNames='bank13', OutputWorkspace='crop')
​
DeleteWorkspace("TOPAZ_36079.nxs_event")
​
#UB = mtd['TOPAZ_36079.nxs_peaks'].sample().getOrientedLattice().getUB()
#print(UB)
​
​
​
#RemoveLogs(Workspace="crop")
​
# try to make test file really small by including a small detector range around each peak
# DET IDS to use
# peak 0: 858225
# peak 1: 905237
# peak 2: 874008
# todo: build from peak ws directly
detids = [858225, 905237, 874008]
​
ExtractSpectra(InputWorkspace="crop",
               OutputWorkspace="crop",
               DetectorList="858220-858230, 905232-905242, 874003-874013") # +/- 5 detectors around each detid
             
​
UB = np.array([[ 0.15468228,  0.10908475, -0.14428671],
               [-0.08922105, -0.08617147, -0.22976459],
               [-0.05616441,  0.12536522, -0.03238277]])
​
ConvertToMD(InputWorkspace='crop', 
            QDimensions='Q3D', 
            dEAnalysisMode='Elastic',
            Q3DFrames='Q_sample', 
            LorentzCorrection=True, 
            OutputWorkspace='md', 
            #MinValues='-12,-12,-12', 
            #MaxValues='12,12,12')
            MinValues='1,1,1.675', # closer crop to the data
            MaxValues='10,5,8.425')
            
CreatePeaksWorkspace(InstrumentWorkspace='crop', NumberOfPeaks=0, OutputWorkspace='peaks')
​
SetUB('peaks', UB=UB)
​
AddPeakHKL('peaks', [0.15, 1.85, -1])
AddPeakHKL('peaks', [1, 4, -3])
AddPeakHKL('peaks', [1, 5, -3])
​
IndexPeaks(PeaksWorkspace='peaks', 
           Tolerance=0.06, 
           ToleranceForSatellite=0.05, 
           RoundHKLs=False, 
           ModVector1='0.125,0,0', 
           ModVector2='0,0.125,0', 
           ModVector3='-0.125,0.125,0', 
           MaxOrder=1, 
           CrossTerms=False, 
           SaveModulationInfo=True)
​
# ----------------------------------------------------------------------------           
# run algorithm for testing --------------------------------------------------
# ----------------------------------------------------------------------------
​
# run algorithm WITHOUT new satellite options for comparing
IntegrateEllipsoids(InputWorkspace='crop', 
                    PeaksWorkspace='peaks', 
                    RegionRadius=0.055, 
                    SpecifySize=True, 
                    PeakSize=0.0425,
                    BackgroundInnerSize=0.043, 
                    BackgroundOuterSize=0.055, 
                    OutputWorkspace='peaks_integrated_nosatellite', 
                    CutoffIsigI=5,
                    UseOnePercentBackgroundCorrection=False)
​
# run WITH new satellite background options to compare to above
# Should check that:
# -- each satellite peak should have NONZERO MNP vector
# -- have the same number of peaks output (3)
# -- integrated intensity of non-satellite peaks (bragg peaks) match previous run
# -- integrated intensity of satellite peaks is set & is different than previous run
# -- algorithm sets
#    "PeaksIntegrated", "SatellitePeakRadius", 
#    "SatelliteBackgroundInnerRadius" and "SatelliteBackgroundOuterRadius" run properties
IntegrateEllipsoids(InputWorkspace='crop', 
                    PeaksWorkspace='peaks', 
                    RegionRadius=0.055, 
                    SpecifySize=True, 
                    PeakSize=0.0425,
                    BackgroundInnerSize=0.043, 
                    BackgroundOuterSize=0.055, 
                    OutputWorkspace='peaks_integrated_satellite', 
                    CutoffIsigI=5,
                    UseOnePercentBackgroundCorrection=False,
                    SatelliteRegionRadius=0.1, 
                    SatellitePeakSize=0.08, 
                    SatelliteBackgroundInnerSize=0.081, 
                    SatelliteBackgroundOuterSize=0.1)
​
​
peaks_nosat = mtd["peaks_integrated_nosatellite"]
peaks_sat   = mtd["peaks_integrated_satellite"]
​
print("testing that properties were set...")
assert peaks_sat.run().hasProperty("PeaksIntegrated")
assert peaks_sat.run().hasProperty("SatellitePeakRadius")
assert peaks_sat.run().hasProperty("SatelliteBackgroundInnerRadius")
assert peaks_sat.run().hasProperty("SatelliteBackgroundOuterRadius")
​
n = peaks_nosat.getNumberPeaks()
for i in range(n):
    peak = peaks_nosat.getPeak(i)
    satpeak = peaks_sat.getPeak(i)
    
    peak_mnp = peak.getIntMNP()
    satpeak_mnp = satpeak.getIntMNP()
    
    peak_int = peak.getIntensity()
    satpeak_int = satpeak.getIntensity()
    
    print("peak {}:".format(i+1))
    print("  NO satellite:   MNP = {}, intensity = {}".format(peak_mnp, peak_int))
    print("  WITH satellite: MNP = {}, intensity = {}".format(satpeak_mnp, satpeak_int))
    
    # Verify that intensities match for non-satellite peaks
    if satpeak_mnp.norm2() == 0.0:
        # this should match since it is using the original shell for integrating the bragg peaks?
        np.testing.assert_almost_equal(peak_int, satpeak_int)