INERTIA = 1.167e6
HEIGHT = 112.5
CENTROID = 73.24
Q = 278
Q_glue = 278
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
  max_stress = K * pi^2 * E / (12 * (1 - MU^2)) * (t / b)^2
end

function fos_thin_plate = find_fos_thin_plate(K, t, b, stress_max)
  fos_thin_plate = stress_max / thin_plate_buckling(K, t, b)
end

# case 1: compressive flange between webs

fos_case1 = find_fos_thin_plate(4, 3*T, BETWEEN_WEB, MAT_COMP)



b1 = 75 - 1.27 % top flange inside
b2 = 12.5 + 1.27 % top flange flaps
b3 = (112.7 - (4 * 1.27)) / 2 % height of web % VERY SUS CHECK THIS OUT
b4 = b3 % sussy
a = 150
failure1 = 4 * (pi^2) * MAT_E * ((T * 3) ^ 2) / (12 * (1 - (MU ^ 2)) * (b1^2))
FOSbuck1 = failure1 / (Mmax * (112.5 - CENTROID) / INERTIA)
failure2 = 0.425 * (pi^2) * MAT_E * (T^2) / (12 * (1 - (MU^2)) * (b2^2))
FOSbuck2 = failure2 / (Mmax * (112.5 - CENTROID) / INERTIA)
failure3 = 6 * (pi^2) * MAT_E * (T^2) / (12 * (1 - (MU^2)) * (b3^2))
FOSbuck3 = failure3 / (Mmax * (CENTROID - (1.27/2)) / INERTIA)
failure4 = (5 * (pi^2) * MAT_E) ./ (12 * (1 - (MU^2))) .* (((2*T)/b4)^2 + ((2*T)./a).^2)
FOSbuck4 = failure4 / shear
