"""
pipeline_config.py
==================
Single source of truth for all pipeline parameters.

Dead-code audit (2026-07-04): removed POSTPROCESS_N, SWEEP_V_MIN, SWEEP_V_MAX and
SWEEP_RPM_MIN (assigned in NB6/NB6b but never read), and the MEASURED_MASS_INERTIA_CSV /
VALIDATION_GEOMETRY_CSV / VALIDATION_PREFIX constants (duplicated ownership --
utils/measurements.py is the single owner of the measured-data filenames).

Every notebook imports from here:

    import pipeline_config as cfg

Changing a value here propagates automatically to NB4, NB5, NB6, NB7, and NB8.
Re-run the affected notebooks after any change.

Sections
--------
1. Operating envelope   - RPM range, launch RPM, velocity grid
2. Physical constants   - air properties, gravity
3. Geometry anchors     - radial station positions (must match NB3)
4. XFoil settings       - Re grid, transition, alpha sweep, gates
5. QProp settings       - grid, plausibility gates, parallelism
6. Flight dynamics      - ODE solver, drag model, output columns
7. Representative selection - band sizes, T/W window, geo features
8. Output CSV names     - all pipeline CSV filenames in one place
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# 1. OPERATING ENVELOPE
# ---------------------------------------------------------------------------

# QProp sweep RPM grid (NB5) and Re derivation bounds (NB4)
#
# IMPORTANT (audit 2026-06): the QProp sweep file (05_qprop_sweep.csv.gz) must be
# regenerated whenever this RPM range changes. NB6 reads the sweep's actual RPM
# ceiling and REFUSES to run any launch RPM above it (no silent extrapolation).
# If you change RPM_MIN/RPM_MAX here, re-run NB5 with QPROP_OVERWRITE_RUNS=True
# before NB6 so the sweep covers the new range.
#
# Operating range set to 1500-6500 RPM (2026-06): the launcher rig does not operate
# reliably below 1500 RPM, so the design/operating envelope starts there.
RPM_MIN   = 1500    # [rev/min]  lower bound
RPM_MAX   = 6500    # [rev/min]  upper bound
RPM_STEP  = 500     # [rev/min]  step size for QProp hover/flight grids

# Reference launch RPM used by NB7 representative selection and NB5 optima extraction.
# NB6 also writes 06_flight_dynamics.csv at this RPM for NB7 compatibility.
LAUNCH_RPM      = 4000.0  # [rev/min]
RPM_TOL         = 100.0   # [rev/min]  tolerance window around LAUNCH_RPM for NB5 optima

# NB6 launch RPM sweep - runs full flight simulation at each RPM, saves one CSV per RPM
LAUNCH_RPM_MIN  = 1500    # [rev/min]  (matches operating range floor)
LAUNCH_RPM_MAX  = 6500    # [rev/min]
LAUNCH_RPM_STEP = 500     # [rev/min]

# Velocity grid for QProp forward-flight sweep (NB5)
FLIGHT_V_MIN  = 0.5   # [m/s]
FLIGHT_V_MAX  = 10.0  # [m/s]
FLIGHT_V_STEP = 0.5   # [m/s]

# ---------------------------------------------------------------------------
# 2. PHYSICAL CONSTANTS
# ---------------------------------------------------------------------------

GRAVITY_M_S2            = 9.81       # [m/s^2]
AIR_DENSITY_KG_M3       = 1.225      # [kg/m^3]  ISA sea level
AIR_KINEMATIC_VISCOSITY = 1.5e-5     # [m^2/s]   air at 20 C

# ---------------------------------------------------------------------------
# 3. GEOMETRY ANCHORS  (must match NB3 / NB4 exactly)
# ---------------------------------------------------------------------------

INNER_ANCHOR_RADIUS_MM  = 4.0    # inboard end of chord/twist spline [mm]
HUB_STATION_RADIUS_MM   = 8.25   # aerodynamic root station for QProp [mm]

QPROP_STATION_FRACTIONS = [0.20, 0.35, 0.50, 0.65, 0.80, 0.92]  # r/R
QPROP_STATION_NAMES     = ["s1", "s2", "s3", "s4", "s5", "s6"]

# ---------------------------------------------------------------------------
# 4. XFOIL SETTINGS  (NB4)
# ---------------------------------------------------------------------------

NB4_MAX_RPM_FACTOR     = 1.15     # max_rpm = LAUNCH_RPM * this (15% overspeed margin)
NB4_FLOOR_RPM          = RPM_MIN  # lower RPM for Re grid derivation

RE_FLOOR               = 10_000   # hard lower bound for XFoil runs
RE_CEILING             = 500_000  # hard upper bound
RE_ROUNDING_STEP       = 5_000    # round Re to nearest N for cache reuse
RE_SAMPLES_PER_DECADE  = 4        # log-spaced XFoil points per Re decade

NCRIT            = 5        # eN amplification factor (indoor enclosed environment)
XTR_OUTER        = 0.05     # forced transition for Re > HUB_RE_THRESHOLD
XTR_HUB          = 0.01     # forced transition for Re <= HUB_RE_THRESHOLD
HUB_RE_THRESHOLD = 15_000   # Re boundary between xtr_outer and xtr_hub

ALPHA_START           = -5.0   # [deg]
ALPHA_END             = 18.0   # [deg]
ALPHA_STEP            =  0.5   # [deg]
XFOIL_MAX_ITERATIONS  = 500
XFOIL_TIMEOUT_SEC     = 60
XFOIL_FIT_ALPHA_LOW   =  0.0   # [deg]
XFOIL_FIT_ALPHA_HIGH  =  8.0   # [deg]
XFOIL_MIN_POINTS_FIT  =  4

CLA_MINIMUM          = 1.5
CLA_MAXIMUM          = 8.5
CD0_MINIMUM          = 0.003
CD0_MAXIMUM          = 0.20
CD0_REFERENCE_CL     = 0.5
STALL_SAFETY_BUFFER  = 0.05
CL_JUMP_THRESHOLD    = 0.6
MIN_VALID_POLAR_ROWS = 5
MIN_VALID_FILE_BYTES = 400

RE_EXPONENT_R2_GATE  = 0.85   # fall back to -0.5 if R^2 below this

QPROP_AERO_KEYS = [
    "CL0", "CL_a", "CLmin", "CLmax",
    "CD0", "CD2u", "CD2l", "CLCD0",
    "REref", "REexp", "xfoil_ok",
]

# ---------------------------------------------------------------------------
# 5. QPROP SETTINGS  (NB5)
# ---------------------------------------------------------------------------

QPROP_MIN_CONFIDENCE = 0.80
QPROP_MIN_STATIONS   = 3

QPROP_T_MAX_N        = 20.0   # [N]   plausibility gate
QPROP_P_MAX_W        = 300.0  # [W]   plausibility gate

QPROP_MAX_WORKERS    = 16
QPROP_TIMEOUT_SEC    = 10
QPROP_OVERWRITE_RUNS = False

# ---------------------------------------------------------------------------
# 6. FLIGHT DYNAMICS  (NB6)
# ---------------------------------------------------------------------------

INITIAL_HEIGHT_M              = 0.0
INITIAL_VERTICAL_VELOCITY_M_S = 0.0

# Body-drag coefficient for the bluff structure the axial flow sees (ring rim,
# hub, blades edge-on). Applied to the COMPUTED axial frontal area in NB6, NOT to
# the blade planform. The blades' own aerodynamic drag is already inside QProp's
# T(V,ω) (blade-element/momentum), so it must not be added a second time here.
#
# 1.1 is the canonical drag coefficient for a short circular cylinder / annular
# rim in axial (cross-) flow at this Reynolds number (Hoerner, Fluid-Dynamic
# Drag, 1965). The previous value 1.17 (flat plate NORMAL to flow) applied to the
# blade planform double-counted blade drag and used a ~3x too-large area.
BODY_DRAG_COEFFICIENT = 1.1   # cylinder/annulus Cd for ring+hub bluff body

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
# 7. REPRESENTATIVE SELECTION  (NB7)
# ---------------------------------------------------------------------------

N_BAND0  = 8
N_BAND1  = 92
N_TIERS  = 4

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
# 8. OUTPUT CSV NAMES
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

# Measured input data enters the pipeline through utils/measurements.py, which owns
# the canonical filenames (utils/00_measured_mass_inertia.csv, utils/00_validation_geometry.csv).
# The 10 recovered validation props are re-simulated by NB3-NB6b and written next to
# the main outputs with a "val_" prefix, e.g. val_04_xfoil_polars.csv.

# ---------------------------------------------------------------------------
# Derived convenience values
# ---------------------------------------------------------------------------

import math

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


# ---------------------------------------------------------------------------
# NB1 - constrained LHS sampling of the design space
# ---------------------------------------------------------------------------

SLIDER_BOUNDS = {                       # (min, max) of every Propeller Configurator slider
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

N_SAMPLES              = 5000    # size of the design space
GLOBAL_RANDOM_SEED     = 99      # numpy global seed (reproducibility)
RADIUS_BLADE_LHS_SEED  = 99      # LHS seed, radius x blade-count plane
GEOMETRY_LHS_SEED      = 456     # LHS seed, remaining 13 geometry dims

MIN_ABS_WALL_THICKNESS_MM = 1.0  # printability floor at every station [mm]
INNER_SOLIDITY_MAX        = 0.7  # chord*blades / circumference cap at the inner station
MID_SOLIDITY_MAX          = 0.85 # same cap at the mid station

SAMPLING_REFERENCE_RPM   = 4000  # operating point for the AoA feasibility window [rev/min]
SAMPLING_V_AXIAL_M_PER_S = 1.0   # assumed axial inflow at that point [m/s]
AOA_MIN_DEG              = 0.0   # per-station angle-of-attack window at the
AOA_MAX_DEG              = 12.0  #   reference point (keeps sections attached)
ENFORCE_MONOTONIC_TWIST  = True  # inner angle >= mid angle >= outer angle

ANGLE_INTERPOLATION_METHOD = "natural_cubic_spline_three_profiles"
ANGLE_SPLINE_BC_TYPE       = "natural"

# ---------------------------------------------------------------------------
# NB2 - RhinoCompute STL generation
# ---------------------------------------------------------------------------

RHINO_COMPUTE_URL     = "http://localhost:5000/"
RHINO_COMPUTE_API_KEY = ""
RHINO_COMPUTE_EXE     = r"%APPDATA%\McNeel\Rhinoceros\packages\8.0\Hops\0.16.28\rhino.compute\rhino.compute.exe"
GH_FILE_NAME          = "Propeller_Raul_V1.2.gh"   # parametric generator, lives in utils/

NB2_MAX_CONFIGS       = None   # cap for test runs; None = all
NB2_MAX_WORKERS_CAP   = 16     # parallel RhinoCompute calls (min with cpu count)
GENERATION_PASSES     = 3      # retry passes over failed meshes
RUN_SINGLE_TEST_FIRST = True   # solve one config before the batch
TEST_CONFIG_INDEX     = 0
EXPORT_SOLUTION       = True
POSITION_OFFSET       = 50     # Grasshopper placement offset
STL_OK_MIN_L          = 0.0035 # minimum plausible enclosed volume [L]

CSV_TO_GH = {                  # geometry CSV column -> Grasshopper input name
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
# NB3 / NB9 - STL lookup
# ---------------------------------------------------------------------------

STL_FILENAME_PATTERNS = [        # tried in order when locating a config's mesh
    "prop_{config_id}.stl",
    "{config_id}.stl",
    "config_{config_id}.stl",
    "Prop_{config_id}.stl",
]

# ---------------------------------------------------------------------------
# NB4 - execution
# ---------------------------------------------------------------------------

XFOIL_MAX_WORKERS_CAP = 16     # parallel XFoil processes (min with cpu count)

# ---------------------------------------------------------------------------
# NB6b / NB8 / NB9 - launcher-run cleaning and release model
# (the raw runs themselves live in utils/results/, see utils/measurements.py)
# ---------------------------------------------------------------------------

RELEASE_CORRECTION_FALLBACK = (0.2322, 0.1675)  # (A, B) used only if no runs are present

RUN_MAX_CLIMB_SPEED_MS  = 8.0    # kinematic glitch rejection: max plausible climb speed
RUN_PEAK_DWELL_S        = 0.05   # peak must persist this long to count
RUN_PEAK_NEAR_FRACTION  = 0.70   # samples near the peak must reach this fraction of it
RUN_RPM_FREEZE_WINDOW   = 15     # samples over which the RPM reading must be frozen
RUN_RPM_FREEZE_TOL      = 1.0    # [rev/min] tolerance for "frozen"

LIFTOFF_HEIGHT_M  = 0.05         # below this a launch counts as no lift-off
HEIGHT_CEILING_M  = 2.60         # physical string ceiling of the launcher
CENSOR_AT_M       = 2.40         # measured peaks above this are right-censored
KICK_VELOCITY_MS  = 1.9          # upward release kick evidenced by the traces [m/s]
V_ENVELOPE_MS     = 5.0          # void-free QProp envelope bound for the NB9 robustness check

# ---------------------------------------------------------------------------
# NB9 - validation switches
# ---------------------------------------------------------------------------

VALIDATE_SIM             = "release"  # which sim the headline metrics use ('release' or 'aero')
USE_REGRESSED_TARGET     = True       # isotonic-regressed PASS-mean as the measured target
USE_RPM_CONFIRMED_PEAKS  = True       # frozen-RPM + kinematic glitch rejection of run peaks
VALIDATION_GRAVITY_M_S2  = 9.80665    # standard gravity; NB9 deliberately keeps its own
                                      #   value (vs GRAVITY_M_S2) as an independence check

# ---------------------------------------------------------------------------
# NB8 - figure output and spin-retention recompute
# ---------------------------------------------------------------------------

NB8_HIRES_DPI      = 300         # dpi of the high-resolution results figures
RETENTION_LAUNCH_M = 0.05        # min lift height for a run to enter the retention curve
PLATEAU_FRAC       = 0.90        # fraction of the pre-release RPM plateau used as reference
JOINT_WINDOW_S     = 1.0         # window around release for the joint RPM estimate [s]
RETENTION_MIN_CONF = 5           # min confident samples per target-RPM bin

# ---------------------------------------------------------------------------
# Quick self-test:  python pipeline_config.py
# ---------------------------------------------------------------------------

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
