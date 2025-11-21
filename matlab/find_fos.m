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

shear = Vmax *

% euler buckling

p_euler = pi ^ 2 * E * INERTIA / (BRIDGE_LEN ^ 2)
fos_euler_buckling = p_euler / MAX_LOAD

mu = 0.2
centroid = 73.34
t = 1.27
b1 = 75 - 1.27 % top flange inside
b2 = 12.5 + 1.27 % top flange flaps
b3 = (112.7 - (4 * 1.27)) / 2 % height of web % VERY SUS CHECK THIS OUT
b4 = b3 % sussy
a = 150
failure1 = 4 * (pi^2) * MAT_E * ((t * 3) ^ 2) / (12 * (1 - (mu ^ 2)) * (b1^2))
FOSbuck1 = failure1 / (max_moment * (112.5 - centroid) / INERTIA)
failure2 = 0.425 * (pi^2) * MAT_E * (t^2) / (12 * (1 - (mu^2)) * (b2^2))
FOSbuck2 = failure2 / (max_moment * (112.5 - centroid) / INERTIA)
failure3 = 6 * (pi^2) * MAT_E * ((2*t)^2) / (12 * (1 - (mu^2)) * (b3^2))
FOSbuck3 = failure3 / (max_moment * (centroid - (1.27/2)) / INERTIA)

failure4 = (5 * (pi^2) * MAT_E) ./ (12 * (1 - (mu^2))) .* (((2*t)/b4)^2 + ((2*t)./a).^2)
FOSbuck4 = failure4 / shear
