# vakkenpakketten
Generator voor mogelijke vakkenpakketten.

## Quick start

Run:

```bash
python generate_vwo_packages.py
```

This creates `vwo_packages.txt` with one package per line.

## Output format

- Subject abbreviations only
- `+` as separator
- Alphabetical order per package
- Package size: 8 or 9 subjects

Example:

```txt
econ+entl+gtc+nat+netl+schk+wisb+wisd
```

## Rules currently encoded (VWO)

- Legal profile structure for `nt`, `ng`, `em`, `cm` (based on article 2.5 to 2.7)
- School exclusion pairs from the Profielkeuze page text
- School note for NT: modern language choice limited to French/German
- Extra school rules from `Lessentabel_vwo.jpg`, including:
	- `netl` and (`entl` or `ct`) in the common part
	- tighter profile-vak combinations per profile
	- profile-specific vrije-deel constraints

## Data structure choices

- One package is represented as a `set[str]` during validation and generation:
	- Fast membership checks (`in`), subset checks, and pair-exclusion checks.
	- No duplicate subjects possible by construction.
- Persisted output uses a canonical `str` line (`+`-joined sorted subjects):
	- Easy to compare, sort, deduplicate, and write to text file.
- All generated packages are stored in a `set[str]`:
	- Prevents duplicates across profiles automatically.

## Confirmed scope

- No separate modeling for atheneum and gymnasium (single VWO model only).
- No subject-specific personal preconditions (for example prior-year participation or grade thresholds).
- The script is intentionally simple and can be extended with extra rules later.

## Current interpretation notes

- The table label `vrije deel (2)` is interpreted as: each package must contain exactly two subjects from the profile-specific vrije-deel options.
- If you want a stricter interpretation (for example exact option blocks), this can be added.
