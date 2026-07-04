# Cleaned Propeller Test Data — Info for Hector

## What these files are
Each `*_cleaned.csv` is the processed output of a single propeller test run
(raw laser + TFMini distance sensor log -> cleaned time/RPM/height series),
ready to use directly.

## Filename convention
Raw and cleaned files follow:

```
PROPID_BLADENR_RPMATLAUNCH_RUNNR.csv
PROPID_BLADENR_RPMATLAUNCH_RUNNR_cleaned.csv
```

- **PROPID** — propeller identifier
- **BLADENR** — number of blades
- **RPMATLAUNCH** — target/commanded RPM for this run
- **RUNNR** — repetition number (1, 2, 3, ...) for that prop/RPM combo

Example: `1093_5_4500_2_cleaned.csv` = propeller 1093, 5 blades, target 4500 RPM, run 2.

## Columns
| Column | Meaning |
|---|---|
| `time_s` | Time in seconds. **t = 0 is the launch moment** (when the propeller first sustainably lifts off). Negative values = pre-launch (sitting on the ground before takeoff). |
| `rpm` | Propeller RPM, computed from laser blade-crossing intervals and interpolated onto the TFMini sample times. Can be empty/NaN if the laser didn't register enough crossings for that run. |
| `height_m` | Height above the launch point, in meters (0 = ground/launch height). |

## Header comment lines
Each file starts with 1-2 `#` comment lines and ends with a `#` summary line:

```
# filter: <filtering parameters used to produce this file>
# comment: <optional note from the test run plan, if any; this was in case Alexandra observed something she thinks was important for interpreting later on>
... data ...
# max_height_m=1.23, flight_time_s=2.45, mean_rpm=3200, prop_id=1093, blade_nr=5, target_rpm=4500, run_nr=2
```

The last line gives you the **max height**, **flight duration**, **mean RPM**, and the
propeller/run identifiers without needing to parse the whole file.

## Important note on `time_s = 0`
For a small number of runs, the propeller never produced enough lift to "launch"
(it never left the ground). For those files, `t = 0` instead just marks the
**start of the recording** (not a launch), and `height_m` is the raw measured
distance rather than height-above-launch. You can check `cleaning_report.csv`
(see below) to see which files this applies to.

## Other files in this folder
- **`cleaning_report.csv`** — one row per input file: `OK` (launch detected,
  cleaned normally), `WARNING` (no launch detected — see note above), or
  `ERROR` (file couldn't be processed, with reason).
- **`cleaned_validation_report.csv`** — automated quality check on the cleaned
  files (PASS/REVIEW/FAIL per file), useful for spotting runs that may need a
  closer look (e.g. implausible max height, missing RPM, etc.).

## Batch 1 validation results — files that need a closer look
Running the cleaned-CSV validation on batch 1 (274 files) gave
**161 PASS / 92 REVIEW / 21 FAIL**. Breakdown:

**REVIEW (92 files, only 1 of 5 checks failed):**
- **77 files** fail only `rpm_mean_ok` — mean RPM differs from the target by
  50–93% (median ~64%). This is expected: it's the startup spin-up procedure,
  so these are likely fine to use as-is.
- **14 files** fail only `max_height_plausible` — max height ≈ 0
  (0.0000–0.04 m). The propeller never produced enough lift to leave the
  ground at that RPM.
- **1 file** (`3243_6_1500_1`) fails only `height_normalized` — same
  "barely lifted off" situation (max height 0.064 m).

**FAIL (21 files, ≤3 of 5 checks passed):**
- **20 files** — all 19 runs of **propeller 685** plus `868_3_1500_3` — have
  `mean_rpm = NaN`. E.g. `685_4_3000_2.csv` has 4840 TFMini rows but only
  **1 laser row** in the whole recording, so RPM can't be computed at all.
  This is a sensor/data-collection issue specific to those recordings, not a
  cleaning bug — height data for these files is still fine.
- **1 file** (`1093_5_4500_3`) — max height ≈ 0 *and* the same RPM spin-up
  deviation as above.

**How to interpret the "never lifted off" files** (max height ≈ 0, ~15 files
across REVIEW/FAIL, plus the 15 similar files in batch 2 — see
`02_PropellerTesting_SecondBatch_cleaned\cleaning_report.csv`): these line up
with high blade-count propellers at low RPM (more blades = more drag = needs
higher RPM to lift), which looks like a real physical result (below the
lift-off threshold for that prop/RPM combo) rather than a data error. They're
kept in the dataset as "no-flight" runs — `cleaning_report.csv` and
`cleaned_validation_report.csv` flag which files these are.

## Batch 2 validation results — files that need a closer look
Running the cleaned-CSV validation on batch 2 (600 files) gave
**354 PASS / 231 REVIEW / 15 FAIL**. Breakdown:

**REVIEW (231 files, only 1 of 5 checks failed):**
- **175 files** fail only `rpm_mean_ok` — mean RPM differs from the target by
  50–97% (median ~65%). Same startup spin-up effect as batch 1 — likely fine
  to use as-is.
- **49 files** fail only `max_height_plausible` — max height between 0 and
  0.049 m, i.e. right around (and just under) the 0.05 m lift-off threshold.
  Same "barely got off the ground" situation as batch 1.
- **7 files** fail only `height_normalized` — max height ~0.05 m, right at
  the threshold. These are part of the 15 "no launch detected" files (see
  `02_PropellerTesting_SecondBatch_cleaned\cleaning_report.csv`), where
  `height_m` isn't baseline-normalized.

**FAIL (15 files, ≤3 of 5 checks passed):**
- **2 files** (`178_6_6000_3`, `739_3_2500_1`) have `mean_rpm = NaN` —
  same sensor issue as propeller 685 in batch 1 (laser barely registered
  blade crossings). Height data is still fine.
- **13 files** fail `max_height_plausible` (combined with `height_normalized`
  and/or `rpm_mean_ok`) — these are the rest of the 15 "no launch detected"
  files plus a few extra near-zero-height runs.

**Extra note for batch 2 — propellers 394 and 60:** unlike batch 1, where the
near-zero-height runs were mostly at the *lowest* tested RPMs, propellers
**394** (6 blades) and **60** (6 blades) show max height ≈ 0.01–0.03 m even
at 4500–5500 RPM (`394_6_4500_1`, `394_6_4500_2`, `394_6_5500_2`,
`60_6_4500_2`, `60_6_5000_3` — all FAIL). These had a launch detected, but
barely any height gain across most/all of their RPM range. Worth a closer
look at whether these two propellers (both 6-blade) just don't generate
meaningful lift in this test setup at all, rather than only below a
threshold RPM.

## What `SLS_PropellerTesting_FirstBatch_filled.xlsx` / `SecondBatch.xlsx` are
These are the **run plans/logs** for each test batch — one row per test run,
listing Prop ID, Blade Nr, Run Nr, target RPM at launch, which launcher pin
was used, whether the run was completed, the resulting CSV filename, and any
comments noted during testing (e.g. issues observed on that run). They're the
source of the `# comment:` lines that appear in some cleaned CSVs. Not needed
to use the cleaned data, but useful as a reference for what was actually done
during each run and why a particular run might look unusual.
