INERTIA = 1.167e6
HEIGHT = 112.5
CENTROID = 73.24
Q = 278
WEB_THICK = 2 * 1.27
BRIDGE_LEN = 1200

LOAD_CASE = 300
MAX_LOAD = LOAD_CASE + 1.1 * LOAD_CASE + 1.1 * 1.35 * LOAD_CASE

[M, V, loc] = find_moment_shear(INERTIA, LOAD_CASE);

Mmax = max(M)
Vmax = max(V)

GLUE_SHEAR = 2;
MAT_SHEAR = 4;
MAT_TEN = 30;
MAT_COMP = 6;
MAT_E = 4000;
E = 4000

% comp tension fos

stress_tension = Mmax * CENTROID / INERTIA
stress_comp = Mmax * (HEIGHT - CENTROID) / INERTIA
fos_tension = MAT_TEN / stress_tension
fos_comp = MAT_COMP / stress_comp

% shear fos

shear = Vmax * Q / INERTIA / WEB_THICK;
fos_shear = MAT_SHEAR / shear

% glue shear fos

% WILL NOT FAIL

% euler buckling

p_euler = pi ^ 2 * E * INERTIA / (BRIDGE_LEN ^ 2)
fos_euler_buckling = p_euler / MAX_LOAD


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
