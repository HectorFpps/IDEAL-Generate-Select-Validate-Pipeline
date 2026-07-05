"""
measurements.py
===============
Single access point for all physically measured data used by the pipeline.

All measured inputs live in ``utils/`` — the folder for everything the
pipeline *uses* but never *generates* (measured data, the Grasshopper
definition, the solver executables). Three measured datasets exist:

1. ``utils/00_measured_mass_inertia.csv``
   Bench measurements for every fabricated propeller: the mass from the
   precision scale (``mass_g``) and the trifilar-pendulum oscillation time
   (``T_meas``, seconds for 10 oscillations). NB3 uses these to calibrate
   the SLS print density and the linear inertia correction, and NB9 uses
   them to validate the mass and inertia models.

2. ``utils/00_validation_geometry.csv``
   The explicit, unambiguous ID-to-geometry mapping for the 30 physically
   flight-tested propellers. A re-run of the LHS sampling (NB1) reassigned
   config_ids to new geometries, so for 10 early-printed props the row in
   ``csv/01_geometry.csv`` no longer describes the part that was actually
   printed and tested. This file resolves the ambiguity: each row carries
   the true geometry of the tested part together with a ``geometry_source``
   column ('main_geometry_table' for the 20 representative props, or
   'validation_sample' for the 10 recovered props) and an ``stl_source``
   column naming the folder that holds the printed part's STL.

3. ``utils/results/``
   The raw launcher test campaigns: per-run flight traces
   (``<id>_<blades>_<rpm>_<run>_cleaned.csv``) in the ``*_cleaned``
   batch folders, each with a ``cleaned_validation_report.csv``. NB6b
   fits the release correction on them, NB8 recomputes the spin-retention
   curve from them, and NB9 validates the simulated heights against them.

This module also owns the trifilar-pendulum rig constants and the
period-to-inertia conversion, so NB3 and NB9 share one definition.
"""

from pathlib import Path

import numpy as np
import pandas as pd

MEASURED_MASS_INERTIA_NAME = '00_measured_mass_inertia.csv'
VALIDATION_GEOMETRY_NAME = '00_validation_geometry.csv'
RESULTS_DIR_NAME = 'results'
CLEANED_RUN_DIR_NAMES = ['01_PropellerTesting_FirstBatch_cleaned', '02_PropellerTesting_SecondBatch_cleaned']

PENDULUM_RADIUS_M = 0.090
PENDULUM_STRING_M = 0.700
PLATE_MASS_KG = 11.7 / 1000
PLATE_TARE_TIME_S = 9.2
OSCILLATION_COUNT = 10
GRAVITY_M_S2 = 9.81


def utils_dir(base_dir):

    return Path(base_dir) / 'utils'


def measured_mass_inertia_path(base_dir):

    return utils_dir(base_dir) / MEASURED_MASS_INERTIA_NAME


def validation_geometry_path(base_dir):

    return utils_dir(base_dir) / VALIDATION_GEOMETRY_NAME


def results_dir(base_dir):
    """Folder holding the raw launcher test campaigns (utils/results)."""

    return utils_dir(base_dir) / RESULTS_DIR_NAME


def cleaned_run_dirs(base_dir):
    """The cleaned launcher-run batch folders, in campaign order."""

    dirs = []
    for name in CLEANED_RUN_DIR_NAMES:
        dirs.append(results_dir(base_dir) / name)

    return dirs


def cleaned_validation_reports(base_dir):
    """The per-batch cleaned_validation_report.csv paths, in campaign order."""

    reports = []
    for run_dir in cleaned_run_dirs(base_dir):
        reports.append(run_dir / 'cleaned_validation_report.csv')

    return reports


def load_measured_mass_inertia(base_dir):
    """Load the raw bench measurements, cleaned but not aggregated.

    Returns a DataFrame with one row per measurement and the columns
    config_id (int), mass_g (float) and T_meas (float, seconds for
    10 oscillations). Rows with a non-numeric id or missing values
    are dropped.
    """

    path = measured_mass_inertia_path(base_dir)
    if not path.exists():
        raise FileNotFoundError(f'Measured mass/inertia CSV not found: {path}')
    raw = pd.read_csv(path)
    required = {'config_id', 'mass_g', 'T_meas'}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f'Missing measured columns: {sorted(missing)}')
    cleaned = raw.copy()
    cleaned['config_id'] = pd.to_numeric(cleaned['config_id'], errors='coerce')
    cleaned['mass_g'] = pd.to_numeric(cleaned['mass_g'], errors='coerce')
    cleaned['T_meas'] = pd.to_numeric(cleaned['T_meas'], errors='coerce')
    cleaned = cleaned.dropna(subset=['config_id', 'mass_g', 'T_meas']).copy()
    cleaned['config_id'] = cleaned['config_id'].astype(int)

    return cleaned


def load_measured_mass_inertia_by_id(base_dir):
    """Load the bench measurements aggregated to one row per config_id.

    Repeated measurements of the same propeller are averaged. Returns the
    columns config_id, mass_g, mass_g_std, T_meas, T_meas_std and
    n_measurements.
    """

    cleaned = load_measured_mass_inertia(base_dir)
    grouped = cleaned.groupby('config_id', as_index=False).agg(mass_g=('mass_g', 'mean'), mass_g_std=('mass_g', 'std'), T_meas=('T_meas', 'mean'), T_meas_std=('T_meas', 'std'), n_measurements=('T_meas', 'size'))

    return grouped


def trifilar_inertia_kg_m2(time_for_oscillations_s, oscillating_mass_kg):
    """Convert a trifilar-pendulum oscillation time into a moment of inertia.

    Takes the measured time for OSCILLATION_COUNT oscillations [s] and the
    total oscillating mass [kg]. Returns the inertia about the vertical
    axis [kg m^2] from the small-angle trifilar relation
    I = T^2 m g r^2 / (4 pi^2 L).
    """

    period_s = time_for_oscillations_s / OSCILLATION_COUNT
    inertia = (period_s ** 2) * oscillating_mass_kg * GRAVITY_M_S2 * (PENDULUM_RADIUS_M ** 2) / (4 * np.pi ** 2 * PENDULUM_STRING_M)

    return inertia


def plate_inertia_kg_m2():
    """Inertia of the empty pendulum plate from its tare measurement."""

    inertia = trifilar_inertia_kg_m2(PLATE_TARE_TIME_S, PLATE_MASS_KG)

    return inertia


def add_measured_izz(measured_df):
    """Add the measured spin-axis inertia to an aggregated measurement table.

    Takes a DataFrame with config_id, mass_g and T_meas (one row per config)
    and returns a copy with the added columns T_period_s, mass_kg_meas,
    m_total_kg, izz_total_meas_kg_m2, izz_meas_kg_m2 (the propeller alone,
    tare subtracted) and izz_plate_kg_m2.
    """

    df = measured_df.copy()
    izz_plate = plate_inertia_kg_m2()
    df['T_period_s'] = df['T_meas'] / OSCILLATION_COUNT
    df['mass_kg_meas'] = df['mass_g'] / 1000.0
    df['m_total_kg'] = df['mass_kg_meas'] + PLATE_MASS_KG
    df['izz_total_meas_kg_m2'] = trifilar_inertia_kg_m2(df['T_meas'], df['m_total_kg'])
    df['izz_meas_kg_m2'] = df['izz_total_meas_kg_m2'] - izz_plate
    df['izz_plate_kg_m2'] = izz_plate

    return df


def load_validation_geometry(base_dir):
    """Load the full ID-to-geometry mapping of the 30 flight-tested props.

    Returns the mapping table with one row per tested config_id, the
    geometry_source and stl_source provenance columns, and the same 17
    geometry parameter columns as csv/01_geometry.csv.
    """

    path = validation_geometry_path(base_dir)
    if not path.exists():
        raise FileNotFoundError(f'Validation geometry CSV not found: {path}')
    table = pd.read_csv(path)
    table['config_id'] = table['config_id'].astype(int)

    return table


def load_recovered_validation_geometry(base_dir):
    """Load only the props whose geometry differs from csv/01_geometry.csv.

    These are the rows with geometry_source == 'validation_sample': the 10
    early-printed props whose config_ids were later reassigned by NB1. The
    validation stages of NB3 to NB6b re-simulate exactly these rows, since
    the main pipeline outputs for their ids describe different geometries.
    """

    table = load_validation_geometry(base_dir)
    recovered = table[table['geometry_source'] == 'validation_sample'].copy()
    recovered = recovered.reset_index(drop=True)

    return recovered


def validation_stl_dir(base_dir):

    return utils_dir(base_dir) / 'validation_stl'
