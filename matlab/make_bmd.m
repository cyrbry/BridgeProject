# all lengths are in mm, mm4, N, etc

%% calculating design 4 moment of inertia_mm

%% BME and SFE calculations

clear, close all;

BRIDGE_LEN = 1250;

weight_loc = [0, 100, 200];
weight_amt = [100, 100, 250];
inertia_mm = 1.167e6;
y_bar_mm = 41.4;

# calculate axle pos relative to LHS
ED_WHEEL = 52;
AX_TO_AX = 176;
CAR_TO_CAR = 164;
TRAIN_REL_POS = [ED_WHEEL AX_TO_AX CAR_TO_CAR AX_TO_AX CAR_TO_CAR AX_TO_AX];
TRAIN_LEN = sum(TRAIN_REL_POS)
TRAIN_REL_POS = cumsum(TRAIN_REL_POS);

FREIGHT_N = 300;
FREIGHT_N = FREIGHT_N / 2;
BACK_MULT = 1.1;
BACK_N = FREIGHT_N * BACK_MULT;
LOCO_MULT = 1.38;
LOCO_N = FREIGHT_N * LOCO_MULT;
TRAIN_WEIGHT = ones(1, 6) .* FREIGHT_N;
TRAIN_WEIGHT(1) = BACK_N;
TRAIN_WEIGHT(2) = BACK_N;
TRAIN_WEIGHT(5) = LOCO_N;
TRAIN_WEIGHT(6) = LOCO_N;
TRAIN_WEIGHT = -1 .* TRAIN_WEIGHT;
TOTAL_TRAIN_WEIGHT = sum(TRAIN_WEIGHT)

# calculate the reaction forces
SUPPORT_L = 25;
SUPPORT_R = 1225;

# find the reaction forces on both sides
START_SIM = -TRAIN_LEN;
END_SIM = SUPPORT_R;
#START_SIM = 500
#END_SIM = 500
STEP_SIM = 10;
reaction = [[]:[]];
steps = START_SIM:STEP_SIM:END_SIM;
max_moment = -1;
max_shear = -1;
for position = steps;
  # find the reaction forces for each step
  train_pos = TRAIN_REL_POS + position; # converts relative train pos to abs
  # filters out axles that are not on the bridge anymore
  # train_pos = train_pos .* (train_pos > SUPPORT_L) .* (train_pos < SUPPORT_R)
  dist_to_lhs = train_pos - SUPPORT_L;
  # checks if the train is on the bridge
  trains_on_bridge = (train_pos > SUPPORT_L) .* (train_pos < SUPPORT_R);
  moments_to_lhs = dist_to_lhs .* TRAIN_WEIGHT .* trains_on_bridge;
  dist_between_support = SUPPORT_R - SUPPORT_L;
  reaction_rhs = sum(moments_to_lhs) / dist_between_support * -1;
  reaction_lhs = -sum(TRAIN_WEIGHT .* trains_on_bridge) - reaction_rhs;

  reaction(1,end+1) = reaction_lhs;
  reaction(2,end) = reaction_rhs;

  # filter the train axles so that only the ones within the range are valid

  train_load = nonzeros(TRAIN_WEIGHT .* trains_on_bridge);
  train_pos = nonzeros(train_pos .* trains_on_bridge);

  force_loc = [SUPPORT_L, train_pos', SUPPORT_R];
  force_loc = repelem(force_loc, 2);
  force_loc = [force_loc, 0];

  shear_n = [reaction_lhs, train_load', reaction_rhs];
  shear_n = repelem(cumsum(shear_n), 2);
  shear_n = [0, shear_n];
  max_shear(end+1) = max(shear_n);

  moment_n = [0];
  moment_loc = force_loc;
  for idx = 1:length(force_loc)-1
    cur_shear = shear_n(idx+1);
    moment_len = force_loc(idx+1) - force_loc(idx);
    moment_n(end+1) = cur_shear * moment_len;
  end
  moment_n = cumsum(moment_n);
  max_moment(end+1) = max(moment_n);

  plot(moment_loc, moment_n) # for the BME
  #plot(force_loc, shear_n) # for the SFE
  hold on

#  shear = [[reaction_lhs, train_load, reaction_rhs],[SUPPORT_L, train_pos, SUPPORT_R]]
#  plot(shear(2,:), shear(1,:))
#  hold on
end

hold off

#plot(steps, reaction(1,:));
#hold on
#plot(steps, reaction(2,:));
#legend("LHS Reaction", "RHS Reaction")
#hold off

max_moment = max(max_moment)
max_shear = max(max_shear)

# DANIEL check compressive strength at the top

# DANIEL check compressive strength at the bottom

# DANIEL check buckling at the top

# YANG check buckling at the bottom and glue

%% Calculate FOS's

MAX_SHEAR_GLUE = 2 % MPA
MAX_SHEAR_MATBOARD = 4 % MPA
GLUE_WIDTH = 20 % mm
TOP_LENGTH = 100 % mm
MAT_THICKNESS = 1.27 % mm
LEG_SEPERATION = 80
LEG_HEIGHT = 75

dimensions = [TOP_LENGTH, LEG_SEPERATION, LEG_HEIGHT, GLUE_WIDTH, MAT_THICKNESS]

q_top_glue = TOP_LENGTH * MAT_THICKNESS
shear_glue = max_moment * q_top_glue / inertia_mm / GLUE_WIDTH

glue_fos = MAX_SHEAR_GLUE / shear_glue

q_bot_matboard = 2 * MAT_THICKNESS * y_bar_mm
shear_matboard = max_moment * q_bot_matboard / inertia_mm / (2 * MAT_THICKNESS)

matboard_fos = MAX_SHEAR_MATBOARD / shear_matboard

# YANG check thin plate buckling everywhere :melt:

plate_loc = [100 200 300 600]





%Variables
matboardtens = 30 %MPa
matboardcomp = 6 %MPa
matboardE = 4000
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











