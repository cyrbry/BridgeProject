INERTIA = 1.167e6
LOAD_CASE = 300
CENTROID = 73.24
MAX_LOAD = LOAD_CASE + 1.1 * LOAD_CASE + 1.1 * 1.35 * LOAD_CASE

[max_moment_var_pos, max_shear_var_pos, loc] = find_moment_shear(INERTIA, LOAD_CASE);
loc = loc(1, (1:end-1))

%positive_moment = max_moment_var_pos > 0;
M = max_moment_var_pos(1, 2:end-1);

GLUE_SHEAR = 2;
MAT_SHEAR = 4;
MAT_TEN = 30;
MAT_COMP = 6;
MAT_E = 4000;

stress_tensile = M * CENTROID / INERTIA;
fos_tension = MAT_TEN ./ stress_tensile
plot(loc, fos_tension)
title("FOS")
xlabel("


positive_shear = max_shear_var_pos > 0;
V = max_shear_var_pos(positive_shear);

%M = max_moment_var_pos;
%V = max_shear_var_pos;

max_moment = max(max_moment_var_pos);
max_shear = max(max_shear_var_pos);


q_bot_matboard = 2 * MAT_THICKNESS * y_bar_mm
shear_matboard = max_moment * q_bot_matboard / inertia_mm / (2 * MAT_THICKNESS)

matboard_fos = MAX_SHEAR_MATBOARD / shear_matboard

matboardtenscomp = [matboardtens; matboardcomp]
contactcem = 2 %MPa
dimensions = [100, 80, 75, 5, 1.27]
y = [dimensions(3) + dimensions(5); 0]
%Graph FOS Stress:
FOStens = 30 ./ ((y_bar_mm) * max_moment / inertia_mm)
FOScomp = 6 ./ (abs(y_bar_mm - (dimensions(3) + dimensions(5))) * max_moment / inertia_mm)
plot(linspace(0, 1250, 215), FOStens)
ylim([0, 50])

FOStensmin = min(abs(FOStens))


plot(linspace(0, 1250, 215), FOScomp)
ylim([0, 50])
xlim([0, 1250])

FOScompmin = min(abs(FOScomp))


%Calculate Buckling:
E = 4000

peuler = pi ^ 2 * E * inertia_mm / (BRIDGE_LEN ^ 2)
