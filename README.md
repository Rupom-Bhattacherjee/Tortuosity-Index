# Tortuosity-Index
## Overview
A customizable tool is developed to estimate 3D tortuosity index (TI) using survey data from directional drilling. 
Tortuosity index is estimated using a real-time 3D tortuosity index (https://doi.org/10.2118/178869-MS), originally developed to capture retinal blood-vessel micro-tortuosity. First the borehole trajectory is transformed into consecutive curve turns by finding inflection points. Inflection points are identified by tracking the curvature changes in inclination and azimuth direction. The number of curve turns, and amplitude of each turns contribute to the overall tortuosity index. Azimuth and inclination deviation are calculated separately and combined into one index for 3D estimation. 

To evaluate if wellbore deviation is responsible for downhole equipment failure, 3D TI of a special well that suffered from artificial lift system (ALS) tubing failure is estimated. TI was calculated using the utility tool developed in this study separately for the vertical and lateral section of the wellbore. It was observed that vertical section of that well was significantly more tortuous than the lateral section, which could be responsible for the ALS failure. The work is then extended to other wells that had ALS failure due to reasons likely related to borehole geometry. The most significant new finding is that certain ALS failure causes such as sucker rod coupling mid-length fatigue fracture and hole in tubing-contact with coupling were more strongly linked to wellbore deviation than the other causes. This insight allows the production engineer to optimize the ALS configurations and deployment techniques to better accommodate varying degrees of wellbore deviation. To evaluate if wellbore geometry has any association with production performance, lateral TI and first year production data of wells from three different fields with same target formation were analyzed. Findings revealed no association between TI and production performance, which is consistent with the findings from previous studies. 

The novelty of this work is the development of such a highly customizable tool that allows calculating the tortuosity index in any section of the wellbore. The source code of the tool is provided so that everyone can benefit from the work.
Besides, for the first time this study explored the effect of wellbore deviation on ALS equipment failure. This will allow the engineers prioritize preventive measures and mitigate risks effectively.

## Code Descriptions

### Tourtuosity_Functions
[Tortousity Functions](./Tortuosity_Functions.py) file has all the functions required to calculate TI. 
Just save this file and use it as a library. Import any functions from here to get desired result. 
This file is also used in backend to create the app. 

### Visualization_functions
[Visualization_functions](./Visualization_Functions.py) has the functions to get the directional drilling survey data by different means (e.g., by wellID, wellname, pad name, etc.)
The [GUI tool](./GUI.py) calls these functions backend to get the data, calculate TI, and make plots. Some functions are deliberately kept filtered to prevent unwanted access to company database.

## Analysis
### The TI APP
The [Tortuosity App](./GUI.py) Pulls survey data from the database and calculates TI.
![image](https://github.com/user-attachments/assets/0521ca42-3388-49c4-9d48-c9dd913e36ee)

It is equipped with:
-Calculating TI any section within the wellbore
-All types of tortuosity (Inclination/Azimuth/3D/Localized)
-Plotting tortuosity profile by well or pad name
-Plotting tortuosity against depth.
-Analyzing what type of tortuosity is more dominant

Comparing Vertical Tortuosity: Older vs. Newer Wells
