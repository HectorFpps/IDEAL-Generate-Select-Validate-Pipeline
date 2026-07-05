"""
pipeline_config.py

All tunable parameters of the pipeline, in one place. Every notebook does

    import pipeline_config as cfg

and reads its settings from here, so a value changed in this file propagates
to all stages. After changing something, re-run the pipeline from the first
notebook that uses it.
"""

import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Operating envelope
# ---------------------------------------------------------------------------

# The launcher rig does not work reliably below 1500 RPM, so the whole
# operating range starts there. Note that NB6 refuses to simulate launch RPMs
# above the ceiling of the QProp sweep, so if this range is widened, NB5 has
# to be re-run first with QPROP_OVERWRITE_RUNS = True.
RPM_MIN   = 1500    # [rev/min]
RPM_MAX   = 6500    # [rev/min]
RPM_STEP  = 500     # [rev/min]

# Reference launch RPM: NB5 extracts its hover optima near this point and NB7
# selects the representative subset on the flight results at this RPM.
LAUNCH_RPM = 4000.0  # [rev/min]
RPM_TOL    = 100.0   # [rev/min] window around LAUNCH_RPM for the NB5 optima

# Launch RPMs simulated by NB6/NB6b (one output CSV per RPM)
LAUNCH_RPM_MIN  = 1500
LAUNCH_RPM_MAX  = 6500
LAUNCH_RPM_STEP = 500

# Forward-flight velocity grid of the QProp sweep
FLIGHT_V_MIN  = 0.5   # [m/s]
FLIGHT_V_MAX  = 10.0  # [m/s]
FLIGHT_V_STEP = 0.5   # [m/s]

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

GRAVITY_M_S2            = 9.81
AIR_DENSITY_KG_M3       = 1.225      # ISA sea level
AIR_KINEMATIC_VISCOSITY = 1.5e-5     # air at 20 C

# ---------------------------------------------------------------------------
# NB1 - constrained LHS sampling
# ---------------------------------------------------------------------------

# (min, max) of every slider of the Propeller Configurator
SLIDER_BOUNDS = {
    "radius_mm":             (60, 80),
    "ring_height_mm":        (4, 10),
    "ring_thickness_mm":     (1, 5),
    "blade_count":           (3, 6),
    "inner_thickness_pct":   (4, 24),
    "inner_max_pos":         (2, 8),
    "inner_camber":          (0, 9),
    "inner_chord_mm":        (5, 11),
    "inner_angle_deg":       (2, 25),
    "mid_radial_pos":        (0.3, 0.7),
    "mid_chord_mm":          (10, 30),
    "mid_angle_deg":         (2, 25),
    "outer_thickness_pct":   (4, 24),
    "outer_max_pos":         (2, 8),
    "outer_camber":          (0, 9),
    "outer_chord_mm":        (10, 30),
    "outer_angle_deg":       (2, 25),
}

N_SAMPLES             = 5000
GLOBAL_RANDOM_SEED    = 99
RADIUS_BLADE_LHS_SEED = 99    # LHS plane: radius x blade count
GEOMETRY_LHS_SEED     = 456   # LHS for the remaining 13 dimensions

# printability and aerodynamic feasibility constraints
MIN_ABS_WALL_THICKNESS_MM = 1.0   # [mm] minimum absolute section thickness
INNER_SOLIDITY_MAX        = 0.7   # chord*blades / circumference at the inner station
MID_SOLIDITY_MAX          = 0.85

# The feasible pitch-angle window at each station keeps the local angle of
# attack between AOA_MIN and AOA_MAX at this reference operating point.
SAMPLING_REFERENCE_RPM   = 4000   # [rev/min]
SAMPLING_V_AXIAL_M_PER_S = 1.0    # [m/s]
AOA_MIN_DEG              = 0.0
AOA_MAX_DEG              = 12.0
ENFORCE_MONOTONIC_TWIST  = True   # inner angle >= mid angle >= outer angle

ANGLE_INTERPOLATION_METHOD = "natural_cubic_spline_three_profiles"
ANGLE_SPLINE_BC_TYPE       = "natural"

# ---------------------------------------------------------------------------
# NB2 - STL generation via RhinoCompute
# ---------------------------------------------------------------------------

RHINO_COMPUTE_URL     = "http://localhost:5000/"
RHINO_COMPUTE_API_KEY = ""
RHINO_COMPUTE_EXE     = r"%APPDATA%\McNeel\Rhinoceros\packages\8.0\Hops\0.16.28\rhino.compute\rhino.compute.exe"
GH_FILE_NAME          = "Propeller_Raul_V1.2.gh"

NB2_MAX_CONFIGS       = None    # limit for test runs, None = all configs
NB2_MAX_WORKERS_CAP   = 16
GENERATION_PASSES     = 3       # retry passes over failed meshes
RUN_SINGLE_TEST_FIRST = True
TEST_CONFIG_INDEX     = 0
EXPORT_SOLUTION       = True
POSITION_OFFSET       = 50
STL_OK_MIN_L          = 0.0035  # [L] below this the mesh is considered broken

# geometry CSV column -> Grasshopper input name
CSV_TO_GH = {
    "radius_mm":           "impellerRadius",
    "ring_height_mm":      "impellerHeight",
    "ring_thickness_mm":   "impellerThickness",
    "blade_count":         "bladeCount",
    "inner_thickness_pct": "innerThickness",
    "inner_max_pos":       "innerMaxPos",
    "inner_camber":        "innerCamber",
    "inner_chord_mm":      "innerChord",
    "inner_angle_deg":     "innerAngle",
    "mid_radial_pos":      "middlePos",
    "mid_chord_mm":        "middleChord",
    "mid_angle_deg":       "middleAngle",
    "outer_thickness_pct": "outerThickness",
    "outer_max_pos":       "outerMaxPos",
    "outer_camber":        "outerCamber",
    "outer_chord_mm":      "outerChord",
    "outer_angle_deg":     "outerAngle",
}

# ---------------------------------------------------------------------------
# Radial stations (shared by NB3 and NB4)
# ---------------------------------------------------------------------------

INNER_ANCHOR_RADIUS_MM  = 4.0    # [mm] inboard end of the chord/twist splines
HUB_STATION_RADIUS_MM   = 8.25   # [mm] aerodynamic root station for QProp

QPROP_STATION_FRACTIONS = [0.20, 0.35, 0.50, 0.65, 0.80, 0.92]  # r/R
QPROP_STATION_NAMES     = ["s1", "s2", "s3", "s4", "s5", "s6"]

# filename patterns tried in order when locating a config's mesh (NB3, NB9)
STL_FILENAME_PATTERNS = [
    "prop_{config_id}.stl",
    "{config_id}.stl",
    "config_{config_id}.stl",
    "Prop_{config_id}.stl",
]

# ---------------------------------------------------------------------------
# NB4 - XFoil
# ---------------------------------------------------------------------------

NB4_MAX_RPM_FACTOR = 1.15     # Re grid extends to LAUNCH_RPM * this (overspeed margin)
NB4_FLOOR_RPM      = RPM_MIN

RE_FLOOR              = 10_000   # XFoil is hopeless below this
RE_CEILING            = 500_000
RE_ROUNDING_STEP      = 5_000    # rounding the target Re makes the cache reusable
RE_SAMPLES_PER_DECADE = 4

NCRIT            = 5        # eN factor for an enclosed indoor environment
XTR_OUTER        = 0.05     # forced transition above HUB_RE_THRESHOLD
XTR_HUB          = 0.01     # forced transition at hub-level Reynolds numbers
HUB_RE_THRESHOLD = 15_000

ALPHA_START          = -5.0   # [deg]
ALPHA_END            = 18.0   # [deg]
ALPHA_STEP           = 0.5    # [deg]
XFOIL_MAX_ITERATIONS = 500
XFOIL_TIMEOUT_SEC    = 60
XFOIL_MAX_WORKERS_CAP = 16

# window of the attached-flow linear fit
XFOIL_FIT_ALPHA_LOW  = 0.0    # [deg]
XFOIL_FIT_ALPHA_HIGH = 8.0    # [deg]
XFOIL_MIN_POINTS_FIT = 4

# physical plausibility gates on the fitted polar
CLA_MINIMUM          = 1.5    # [1/rad]
CLA_MAXIMUM          = 8.5
CD0_MINIMUM          = 0.003
CD0_MAXIMUM          = 0.20
CD0_REFERENCE_CL     = 0.5
STALL_SAFETY_BUFFER  = 0.05
CL_JUMP_THRESHOLD    = 0.6
MIN_VALID_POLAR_ROWS = 5
MIN_VALID_FILE_BYTES = 400

RE_EXPONENT_R2_GATE = 0.85    # below this R^2 the REexp fit falls back to -0.5

QPROP_AERO_KEYS = [
    "CL0", "CL_a", "CLmin", "CLmax",
    "CD0", "CD2u", "CD2l", "CLCD0",
    "REref", "REexp", "xfoil_ok",
]

# ---------------------------------------------------------------------------
# NB5 - QProp
# ---------------------------------------------------------------------------

QPROP_MIN_CONFIDENCE = 0.80   # skip configs whose polar confidence is below this
QPROP_MIN_STATIONS   = 3

# anything above these is a solver artefact, not a 15 g propeller
QPROP_T_MAX_N = 20.0    # [N]
QPROP_P_MAX_W = 300.0   # [W]

QPROP_MAX_WORKERS    = 16
QPROP_TIMEOUT_SEC    = 10
QPROP_OVERWRITE_RUNS = False

# ---------------------------------------------------------------------------
# NB6 / NB6b - flight dynamics
# ---------------------------------------------------------------------------

INITIAL_HEIGHT_M              = 0.0
INITIAL_VERTICAL_VELOCITY_M_S = 0.0

# Drag of the bluff structure the axial flow sees (ring rim, hub, blades
# edge-on), applied to the computed axial frontal area. Cd = 1.1 is the
# standard value for a short cylinder / annular rim in axial flow (Hoerner
# 1965). The blades' own drag is already contained in QProp's T and Q and
# must not be counted again here.
BODY_DRAG_COEFFICIENT = 1.1

TIME_LIMIT_S   = 30.0
ODE_METHOD     = "RK45"
ODE_RTOL       = 1e-5
ODE_ATOL       = 1e-8
ROUND_DECIMALS = 8

SWEEP_RPM_MAX = float(RPM_MAX)

NB6_OUTPUT_COLUMNS = [
    "config_id", "flight_ok", "can_liftoff", "rpm_launch",
    "mass_kg", "inertia_kg_m2", "blade_planform_m2", "frontal_area_drag_m2",
    "T_static_N", "Q_static_Nm", "Pshaft_static_W", "T_over_W",
    "h_max_m", "flight_time_s", "hover_time_s",
    "v_max_m_s", "v_impact_m_s", "rpm_at_impact",
]

# ---------------------------------------------------------------------------
# Launcher runs and release model (NB6b, NB8, NB9)
# The raw runs live in utils/results/, accessed via utils/measurements.py.
# ---------------------------------------------------------------------------

RELEASE_CORRECTION_FALLBACK = (0.2322, 0.1675)  # (A, B) if no runs are available

# spike filter for the launcher traces
RUN_MAX_CLIMB_SPEED_MS = 8.0    # [m/s] faster climbs are sensor glitches
RUN_PEAK_DWELL_S       = 0.05   # [s] a real peak persists at least this long
RUN_PEAK_NEAR_FRACTION = 0.70
RUN_RPM_FREEZE_WINDOW  = 15     # samples with frozen RPM reading around the peak
RUN_RPM_FREEZE_TOL     = 1.0    # [rev/min]

LIFTOFF_HEIGHT_M = 0.05   # [m] below this a launch counts as no lift-off
HEIGHT_CEILING_M = 2.60   # [m] string ceiling of the launcher
CENSOR_AT_M      = 2.40   # [m] measured peaks above this are right-censored
KICK_VELOCITY_MS = 1.9    # [m/s] upward kick the release gives the prop
V_ENVELOPE_MS    = 5.0    # [m/s] void-free QProp envelope for the NB9 check

# ---------------------------------------------------------------------------
# NB7 - representative selection
# ---------------------------------------------------------------------------

N_BAND0 = 8     # near-boundary non-liftoff props
N_BAND1 = 92    # liftoff props, split into N_TIERS h_max tiers
N_TIERS = 4

# T/W window of band 0: the decision boundary where a thrust over-prediction
# would flip the liftoff classification
TW_LO = 0.70
TW_HI = 1.00

GEO_FEATURES = [
    "radius_mm",
    "blade_count",
    "mid_chord_mm",
    "outer_chord_mm",
    "mid_angle_deg",
    "outer_angle_deg",
]

RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# NB8 - figures and spin-retention recompute
# ---------------------------------------------------------------------------

NB8_HIRES_DPI      = 300
RETENTION_LAUNCH_M = 0.05   # [m] minimum lift for a run to enter the retention curve
PLATEAU_FRAC       = 0.90   # fraction of the pre-release RPM plateau used as reference
JOINT_WINDOW_S     = 1.0    # [s] window around release for the joint RPM estimate
RETENTION_MIN_CONF = 5      # minimum confident samples per target-RPM bin

# ---------------------------------------------------------------------------
# NB9 - validation
# ---------------------------------------------------------------------------

VALIDATE_SIM            = "release"   # 'release' or 'aero'
USE_REGRESSED_TARGET    = True        # isotonic-regressed PASS-mean as measured target
USE_RPM_CONFIRMED_PEAKS = True        # frozen-RPM + kinematic rejection of run peaks
VALIDATION_GRAVITY_M_S2 = 9.80665     # NB9 keeps its own g as an independence check

# ---------------------------------------------------------------------------
# Output CSV names
# ---------------------------------------------------------------------------

CSV_NAMES = {
    "geometry"            : "01_geometry.csv",
    "stl_volumes"         : "02_stl_volumes.csv",
    "mass_inertia"        : "03_mass_inertia.csv",
    "naca_codes"          : "03_naca_codes.csv",
    "xfoil_failed"        : "04_xfoil_failed_configs.csv",
    "xfoil_polars"        : "04_xfoil_polars.csv",
    "qprop_results"       : "05_qprop_results.csv",
    "qprop_sweep"         : "05_qprop_sweep.csv.gz",
    "flight_dynamics"     : "06_flight_dynamics.csv",
    "all_subsets"         : "07_all_subsets.csv",
    "selected"            : "07_selected.csv",
    "dataset_full"        : "dataset_full_simulation.csv",
    "dataset_validated"   : "dataset_validated.csv",
}

# The measured inputs (utils/00_*.csv, utils/results/) are owned by
# utils/measurements.py. The validation-subset outputs of NB3-NB6b use the
# same names as above with a "val_" prefix.

# ---------------------------------------------------------------------------
# Derived values
# ---------------------------------------------------------------------------

HOVER_RPMS  = list(range(RPM_MIN, RPM_MAX + 1, RPM_STEP))
FLIGHT_RPMS = list(range(RPM_MIN, RPM_MAX + 1, RPM_STEP))

LAUNCH_RPMS = list(range(LAUNCH_RPM_MIN, LAUNCH_RPM_MAX + 1, LAUNCH_RPM_STEP))

velocity_step_count = round((FLIGHT_V_MAX - FLIGHT_V_MIN) / FLIGHT_V_STEP)
FLIGHT_VS = []
for i in range(velocity_step_count + 1):
    FLIGHT_VS.append(round(FLIGHT_V_MIN + i * FLIGHT_V_STEP, 2))

QPROP_GRID = []
for rpm in HOVER_RPMS:
    QPROP_GRID.append((0.0, rpm))
for v in FLIGHT_VS:
    for rpm in FLIGHT_RPMS:
        QPROP_GRID.append((v, rpm))

LAUNCH_OMEGA = LAUNCH_RPM * 2.0 * math.pi / 60.0   # [rad/s]

NB4_MAX_RPM = int(LAUNCH_RPM * NB4_MAX_RPM_FACTOR)


if __name__ == "__main__":
    print("pipeline_config - parameter summary")
    print(f"  QProp RPM grid  : {RPM_MIN}-{RPM_MAX} step {RPM_STEP}  ({len(HOVER_RPMS)} points)")
    print(f"  Launch RPM (ref): {LAUNCH_RPM}  (omega = {LAUNCH_OMEGA:.2f} rad/s)")
    print(f"  Launch RPM sweep: {LAUNCH_RPMS}  ({len(LAUNCH_RPMS)} RPMs)")
    print(f"  NB4 Re RPM      : {NB4_FLOOR_RPM}-{NB4_MAX_RPM}")
    print(f"  Velocity grid   : {FLIGHT_V_MIN}-{FLIGHT_V_MAX} step {FLIGHT_V_STEP}  ({len(FLIGHT_VS)} points)")
    print(f"  QProp grid      : {len(QPROP_GRID)} pts  ({len(HOVER_RPMS)} hover + {len(FLIGHT_VS)*len(FLIGHT_RPMS)} flight)")
    print(f"  Re floor/ceil   : {RE_FLOOR} / {RE_CEILING}")
    print(f"  Band 0/1        : {N_BAND0} / {N_BAND1}  ({N_TIERS} tiers)")
    print(f"  Sweep RPM max   : {SWEEP_RPM_MAX}")
