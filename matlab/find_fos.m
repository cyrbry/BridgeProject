INERTIA = 0.894e6
CENTROID = 65.8
Q = 259

INERTIA = 0.902e6
CENTROID = 69.8
Q = 268

% constants

HEIGHT = 100
WIDTH = 75
TOP_WIDTH = 100
Q_glue = Q
GLUE_TAB = 50
T = 1.27
WEB_THICK = 2 * T
BRIDGE_LEN = 1200

LOAD_CASE = 300
MAX_LOAD = LOAD_CASE + 1.1 * LOAD_CASE + 1.1 * 1.35 * LOAD_CASE

[M, V, loc] = find_moment_shear(INERTIA, LOAD_CASE);

Mmax = max(M);
Vmax = max(V);

GLUE_SHEAR = 2;
MAT_SHEAR = 4;
MAT_TEN = 30;
MAT_COMP = 6;
MAT_E = 4000;
E = 4000;
MU = 0.2;

% comp tension fos

stress_tension = Mmax * CENTROID / INERTIA;
stress_comp = Mmax * (HEIGHT - CENTROID) / INERTIA;
fos_tension = MAT_TEN / stress_tension
fos_comp = MAT_COMP / stress_comp

% shear fos

shear = Vmax * Q / INERTIA / WEB_THICK;
fos_shear = MAT_SHEAR / shear

% glue shear fos

shear_glue = Vmax * Q / INERTIA / GLUE_TAB;
fos_glue = GLUE_SHEAR / shear_glue

% euler buckling

p_euler = pi ^ 2 * E * INERTIA / (BRIDGE_LEN ^ 2);
fos_euler_buckling = p_euler / MAX_LOAD

function max_stress = thin_plate_buckling(K, t, b)
  E = 4000;
  MU = 0.2;
  max_stress = K * pi^2 * E / (12 * (1 - MU^2)) * (t / b)^2;
end

function max_stress = thin_plate_buckling_shear(K, t, b, a);
  E = 4000;
  MU = 0.2;
  max_stress = K * pi^2 * E / (12 * (1 - MU^2)) * ((t / b)^2 + (t / a)^2);
end

function fos_thin_plate = find_fos_thin_plate(K, t, b, stress_max)
  fos_thin_plate = thin_plate_buckling(K, t, b) / stress_max;
end


function fos_thin_plate = find_fos_thin_plate_shear(K, t, b, a, shear_max)
  fos_thin_plate = thin_plate_buckling_shear(K, t, b, a) / shear_max;
end

# case 1: compressive flange between webs

BETWEEN_WEB = WIDTH - T;
fos_case1 = find_fos_thin_plate(4, 3*T, BETWEEN_WEB, MAT_COMP)

# case 2: buckling at tips

TIP_WIDTH = (TOP_WIDTH - WIDTH) / 2;
fos_case2 = find_fos_thin_plate(0.425, T, TIP_WIDTH, MAT_COMP)

# case 3: variable distributed load along web
HALF_WEB = HEIGHT - 3 * T - CENTROID;
fos_case3 = find_fos_thin_plate(6, T, HALF_WEB, MAT_COMP)

# case 4: shear buckling of the webs (need diaphram)

DIAPHRAM_DIST = 1200 / 8;
HEIGHT_WEB = HEIGHT - 4 * T;
fos_case4 = find_fos_thin_plate_shear(5, T, HEIGHT_WEB, DIAPHRAM_DIST, MAT_SHEAR)
