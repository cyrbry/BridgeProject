# all lengths are in mm, mm4, N, etc

clear, close all;

BRIDGE_LEN = 1250;

weight_loc = [0, 100, 200];
weight_amt = [100, 100, 250];
inertia_mm = 0.418e6;
y_bar_mm = 41.4;

# calculate axle pos relative to LHS
ED_WHEEL = 52;
AX_TO_AX = 176;
CAR_TO_CAR = 164;
TRAIN_REL_POS = [ED_WHEEL AX_TO_AX CAR_TO_CAR AX_TO_AX CAR_TO_CAR AX_TO_AX];
TRAIN_LEN = sum(TRAIN_REL_POS)
TRAIN_REL_POS = cumsum(TRAIN_REL_POS);

FREIGHT_N = 100;
LOCO_MULT = 1.38;
LOCO_N = FREIGHT_N * LOCO_MULT;
FREIGHT_N = FREIGHT_N / 2;
LOCO_N = LOCO_N / 2;
TRAIN_WEIGHT = ones(1, 6) .* FREIGHT_N;
TRAIN_WEIGHT(5) = LOCO_N;
TRAIN_WEIGHT(6) = LOCO_N;
TRAIN_WEIGHT = -1 .* TRAIN_WEIGHT;
TOTAL_TRAIN_WEIGHT = sum(TRAIN_WEIGHT)

# calculate the reaction forces
SUPPORT_L = 25;
SUPPORT_R = 1225;

START_SIM = -TRAIN_LEN;
END_SIM = SUPPORT_R;

#START_SIM = 800
#END_SIM = 800

STEP_SIM = 10;
all_react_lhs = [];
all_react_rhs = [];
steps = START_SIM:STEP_SIM:END_SIM;
for position = steps;
  # find the reaction forces for each step
  train_pos = TRAIN_REL_POS + position; # converts relative train pos to abs
  # filters out axles that are not on the bridge anymore
  # train_pos = train_pos .* (train_pos > SUPPORT_L) .* (train_pos < SUPPORT_R)
  dist_to_lhs = train_pos - SUPPORT_L;
  trains_on_bridge = (train_pos > SUPPORT_L) .* (train_pos < SUPPORT_R);
  moments_to_lhs = dist_to_lhs .* TRAIN_WEIGHT .* trains_on_bridge;
  dist_between_support = SUPPORT_R - SUPPORT_L;
  reaction_rhs = sum(moments_to_lhs) / dist_between_support * -1;
  reaction_lhs = -sum(TRAIN_WEIGHT .* trains_on_bridge) - reaction_rhs;

  all_react_lhs(end+1) = reaction_lhs;
  all_react_rhs(end+1) = reaction_rhs;
end
plot(steps, all_react_lhs);
hold on
plot(steps, all_react_rhs);

legend("LHS Reaction", "RHS Reaction")





