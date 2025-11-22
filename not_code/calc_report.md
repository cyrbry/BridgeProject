# Design Calculations Report

## Hand calcs for Design 0 under 400N load case 1

- just copy /Users/julianmoncarz/University/Year_1/Fall_2025/CIV102_Structures/Bridge Project/not_code/CIV102 Project Team 201 Deliverable 1.pdf here

## Evidence of programming

### Code output for all calculations for Design 0 under a moving 400N train (load case 1).

Assuming we are supposed to show what our code outputs for each step of the calcs we did in Deliverable 0

Inputs to all of this: First wheel at 172mm, loadcase 1, 400N total load, dict describing design 0 (ahh this dict is kinda wrong)

**Section Properties:**
- A = 425.3 mm²
- ȳ = 40.76 mm from bottom
- I = 402793 mm⁴

**Support Reactions:**
- RA (at 25mm) = 208.33 N
- RB (at 1225mm) = 191.67 N

**Shear Force Diagram (SFD):**
- Max shear = 208.33 N at x = 25 mm
- Min shear = -191.67 N at x = 1028 mm

**Bending Moment Diagram (BMD):**
- Mmax = 69325 N·mm at x = 688 mm
- Mmin ≈ 0 N·mm at x = 1238 mm

![SFD and BMD for Design 0, Loadcase 1, first wheel at 172mm](images_for_calc_report/SFD_BMD_design0_loadcase1_172mm.png)

**Flexural Stresses at Mmax:**
- Distance from NA to top = 34.24 mm
- Distance from NA to bottom = 40.76 mm
- σ_top = -12.91 MPa (compression)
- σ_bot = 7.02 MPa (tension)

**Material Capacities:**
- Tensile strength = 30 MPa
- Compressive strength = 6 MPa

**Factor of Safety:**
- FOS compression (top) = 0.465
- FOS tension (bottom) = 4.276 

### SFE and BME of Design 0 for Load Case 1 

/Users/julianmoncarz/University/Year_1/Fall_2025/CIV102_Structures/Bridge Project/not_code/images_for_calc_report/SFE_design0_loadcase1.png

### SFE and BME of  final design under Load Case 2 (assume base case loading of 452N)

/Users/julianmoncarz/University/Year_1/Fall_2025/CIV102_Structures/Bridge Project/not_code/images_for_calc_report/SFE_cigar_loadcase2.png

### FOS values along the bridge for Load Case 1 (assume this for design 0)
/Users/julianmoncarz/University/Year_1/Fall_2025/CIV102_Structures/Bridge Project/not_code/images_for_calc_report/FOS_design0_loadcase1.png

### FOS values along the bridge for final design under Load Case 2 452N. 

/Users/julianmoncarz/University/Year_1/Fall_2025/CIV102_Structures/Bridge Project/not_code/images_for_calc_report/FOS_cigar_loadcase2.png

### Entire script, showing comments, formatting, and user-defined functions. Also indicate the packages you installed as well, such as “NumPy”

make this a github repo with ONLY the needed code to make the above plots
