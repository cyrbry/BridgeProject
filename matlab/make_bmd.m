# all lengths are in mm, mm4, N, etc

BRIDGE_LEN = 1250;

weight_loc = [0, 100, 200];
weight_amt = [100, 100, 250];
inertia_mm = 0.418e6;
y_bar_mm = 41.4;

SUPPORT_L = 25;
SUPPORT_R = 1225;

# calculate axle pos relative to LHS
ED_WHEEL = 52;
AX_TO_AX = 176;
CAR_TO_CAR = 164;
TRAIN_POS = [ED_WHEEL AX_TO_AX CAR_TO_CAR AX_TO_AX CAR_TO_CAR AX_TO_AX];
TRAIN_POS = cumsum(TRAIN_POS)

BASE_N = 400
FREIGHT_N = 100
LOCO_MULT = 1.38
LOCO_N = FREIGHT_N * LOCO_MULT
FREIGHT_N = FREIGHT_N / 2
LOCO_N = LOCO_N / 2
TRAIN_WEIGHT = ones(1, 6) .* FREIGHT_N
TRAIN_WEIGHT(5) = LOCO_N
TRAIN_WEIGHT(6) = LOCO_N




