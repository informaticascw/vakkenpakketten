# vakkenpakketten
Generator voor mogelijke vakkenpakketten.

Gemaakt met veel AI gebruik.

## Quick start

Run:

```bash
python generate_packages.py
```

This creates two files:

- `VWO_packages_2024-2025_packages.txt`
- `VWO_packages_2024-2025_report.txt`

## Configuration

You can quickly adjust these constants at the top of `generate_packages.py`:

- `BASE_FILENAME`: base name for generated files
- `NUMBER_OF_SUBJECTS`: required total number of subjects per package
- `NUMBER_OF_FREE_CHOICE_SUBJECTS`: number of vrije-keuze subjects to include

## Output format

- Package list file:
	- Subject abbreviations only
	- `+` as separator
	- Alphabetical order per package
	- Exactly 9 subjects per package
- Report file:
	- Run configuration
	- Package counts per profile
	- Forbidden pairs
	- Full `PROFILE_RULES` snapshot

Example:

```txt
econ+entl+gtc+nat+netl+schk+wisb+wisd+te
```

## Rules currently encoded (VWO)

- Profiles: `nt`, `ng`, `ngt`, `ema`, `emb`, `cm`
- Common part (`_common.common_groups`):
	- `netl`
	- one of `entl` or `ct`
- Profile part (`profile_groups`): exactly one subject from each profile group
- Free-choice part (`free_groups`):
	- choose exactly 2 free-choice groups (`free_pick_groups = 2`)
	- then choose exactly one subject from each chosen group
- Global filters:
	- exactly 9 subjects
	- forbidden school pairs
	- math constraints (`wisd` requires `wisb`; `wisc` cannot combine with `wisa`)

## Data structure choices

- One package is represented as a `set[str]` during validation and generation:
	- Fast membership checks (`in`), subset checks, and pair-exclusion checks.
	- No duplicate subjects possible by construction.
- Persisted output uses a canonical `str` line (`+`-joined sorted subjects):
	- Easy to compare, sort, deduplicate, and write to text file.
- All generated packages are stored in a `set[frozenset[str]]` internally:
	- Prevents duplicates across profiles automatically.

## Confirmed scope

- No separate modeling for atheneum and gymnasium (single VWO model only).
- No subject-specific personal preconditions (for example prior-year participation or grade thresholds).
- The script is intentionally simple and can be extended with extra rules later.

## Current interpretation notes

- The table label `vrije deel (2)` is interpreted as: each package must contain exactly two vrije-deel subjects, chosen via two selected `free_groups`.
- Group overlap is allowed in config, but duplicates are prevented in generated packages.
