from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple

# All VWO subjects provided by the user.
SUBJECTS: List[str] = sorted(
    [
        "ak",
        "beco",
        "biol",
        "chtc",
        "ct",
        "dutl",
        "econ",
        "entl",
        "fatl",
        "fi",
        "ges",
        "gtc",
        "in",
        "ltc",
        "mu",
        "nat",
        "netl",
        "schk",
        "sptl",
        "te",
        "wisa",
        "wisb",
        "wisc",
        "wisd",
    ]
)

PACKAGE_SIZES: Tuple[int, int] = (8, 9)
OUTPUT_FILE = Path("vwo_packages.txt")

RULES: Dict[str, Dict] = {
    "common": {
        "forbidden_pairs": [
            ["te", "mu"],
            ["in", "mu"],
            ["in", "fi"],
            ["wisd", "fi"],
            ["wisd", "te"],
            ["wisd", "mu"],
            ["in", "ak"],
        ],
        "math_rules": {
            "wisd_requires": "wisb",
            "disallow_if_no_bridge": [
                ["wisa", "wisc"],
            ],
            "bridge_subject": "wisb",
        },
    },
    "profiles": {
        "nt": {
            "required_all": ["netl", "wisb", "nat", "schk"],
            "required_one_of": [
                ["entl", "ct"],
                ["fatl", "dutl", "sptl", "chtc", "gtc", "ltc"],
                ["in", "wisd"],
                {"required_one_of": [["econ", "beco"], ["ak", "in"], ["te"]]},
                {"required_one_of": [["econ", "beco"], ["ak", "in"], ["te"]]},
            ],
            "constraints": {
                "allowed_modern_languages": ["fatl", "dutl"],
            },
        },
        "ng": {
            "required_all": ["netl", "wisa", "biol", "schk", "ak"],
            "required_one_of": [
                ["entl", "ct"],
                ["fatl", "dutl", "sptl", "chtc", "gtc", "ltc"],
                {"required_one_of": [["sptl", "fatl", "dutl", "chtc"], ["econ", "beco"], ["fi"], ["mu"], ["te"]]},
                {"required_one_of": [["sptl", "fatl", "dutl", "chtc"], ["econ", "beco"], ["fi"], ["mu"], ["te"]]},
            ],
            "constraints": {},
        },
        "em": {
            "required_all": ["netl", "ges", "econ", "beco"],
            "required_one_of": [
                ["entl", "ct"],
                ["fatl", "dutl", "sptl", "chtc", "gtc", "ltc"],
                ["wisa", "wisb"],
                {
                    "when_has": ["wisa"],
                    "when_not_has": ["wisb"],
                    "required_one_of": [["sptl", "fatl", "dutl", "chtc"], ["ak"], ["fi"], ["mu"], ["te"]],
                },
                {
                    "when_has": ["wisa"],
                    "when_not_has": ["wisb"],
                    "required_one_of": [["sptl", "fatl", "dutl", "chtc"], ["ak"], ["fi"], ["mu"], ["te"]],
                },
                {
                    "when_has": ["wisb"],
                    "required_one_of": [["nat", "ak", "in"], ["fi"], ["mu"], ["te"]],
                },
                {
                    "when_has": ["wisb"],
                    "required_one_of": [["nat", "ak", "in"], ["fi"], ["mu"], ["te"]],
                },
            ],
            "constraints": {},
        },
        "cm": {
            "required_all": ["netl", "ges", "ak"],
            "required_one_of": [
                ["entl", "ct"],
                ["fatl", "dutl", "sptl", "chtc", "gtc", "ltc"],
                ["wisc", "wisa"],
                ["fi", "te", "mu", "fatl", "dutl", "sptl", "chtc", "gtc", "ltc"],
                {"required_one_of": [["sptl", "fatl", "dutl", "chtc"], ["econ", "beco"], ["fi"], ["mu"], ["te"]]},
                {"required_one_of": [["sptl", "fatl", "dutl", "chtc"], ["econ", "beco"], ["fi"], ["mu"], ["te"]]},
            ],
            "constraints": {},
        },
    },
}


# Legal math combinations based on the VWO free-part rules.
# Allowed pairs: (A, B) and (B, C). Any package with D must include B.
def valid_math_combination(package: Set[str]) -> bool:
    math_rules = RULES["common"]["math_rules"]
    wisd_requires = math_rules["wisd_requires"]
    bridge_subject = math_rules["bridge_subject"]

    if "wisd" in package and wisd_requires not in package:
        return False

    for disallowed_pair in math_rules["disallow_if_no_bridge"]:
        pair_set = set(disallowed_pair)
        if pair_set.issubset(package) and bridge_subject not in package:
            return False

    return True


def has_forbidden_pair(package: Set[str]) -> bool:
    return any(set(pair).issubset(package) for pair in RULES["common"]["forbidden_pairs"])


def valid_nt_language_rule(package: Set[str]) -> bool:
    modern_languages = {"fatl", "dutl", "sptl", "chtc"}
    selected_modern_languages = package.intersection(modern_languages)
    allowed_languages = set(RULES["profiles"]["nt"]["constraints"]["allowed_modern_languages"])
    return selected_modern_languages.issubset(allowed_languages)


def valid_common_requirements(package: Set[str]) -> bool:
    if has_forbidden_pair(package):
        return False

    if not valid_math_combination(package):
        return False

    return True


def _nested_option_matches(package: Set[str], option: object) -> bool:
    if isinstance(option, str):
        return option in package
    if isinstance(option, list):
        return any(subject in package for subject in option)
    return False


def required_one_of_entry_is_valid(entry: object, package: Set[str]) -> bool:
    if isinstance(entry, list):
        return bool(set(entry).intersection(package))

    if isinstance(entry, dict):
        when_has = set(entry.get("when_has", []))
        if when_has and not when_has.issubset(package):
            return True

        when_not_has = set(entry.get("when_not_has", []))
        if when_not_has and when_not_has.intersection(package):
            return True

        options = entry.get("required_one_of", [])
        return any(_nested_option_matches(package, option) for option in options)

    return False


def package_is_valid(profile: str, package: Set[str]) -> bool:
    if len(package) not in PACKAGE_SIZES:
        return False

    if not valid_common_requirements(package):
        return False

    if profile == "nt" and not valid_nt_language_rule(package):
        return False

    rules = RULES["profiles"][profile]
    required_all = set(rules["required_all"])
    if not required_all.issubset(package):
        return False

    for entry in rules["required_one_of"]:
        if not required_one_of_entry_is_valid(entry, package):
            return False

    return True


def generate_for_profile(profile: str) -> Set[str]:
    rules = RULES["profiles"][profile]
    required_all = set(rules["required_all"])
    results: Set[str] = set()

    # Build from required profile subjects and validate all rule groups afterward.
    base = set(required_all)

    if len(base) > max(PACKAGE_SIZES):
        return results

    remaining_subjects = [s for s in SUBJECTS if s not in base]

    for target_size in PACKAGE_SIZES:
        missing = target_size - len(base)
        if missing < 0:
            continue

        for extra in combinations(remaining_subjects, missing):
            package = set(base)
            package.update(extra)

            if package_is_valid(profile, package):
                results.add("+".join(sorted(package)))

    return results


def write_output(packages_all: Set[str], path: Path) -> None:
    sorted_packages = sorted(packages_all)
    path.write_text("\n".join(sorted_packages) + "\n", encoding="utf-8")


def print_summary(
    packages_nt: Set[str],
    packages_ng: Set[str],
    packages_em: Set[str],
    packages_cm: Set[str],
    packages_all: Set[str],
) -> None:
    print("Generated VWO package counts:")
    print(f"- nt: {len(packages_nt)}")
    print(f"- ng: {len(packages_ng)}")
    print(f"- em: {len(packages_em)}")
    print(f"- cm: {len(packages_cm)}")
    print(f"- total unique packages: {len(packages_all)}")
    print(f"Output file: {OUTPUT_FILE}")


def main() -> None:
    packages_nt = generate_for_profile("nt")
    packages_ng = generate_for_profile("ng")
    packages_em = generate_for_profile("em")
    packages_cm = generate_for_profile("cm")
    packages_all = packages_nt | packages_ng | packages_em | packages_cm

    write_output(packages_all, OUTPUT_FILE)
    print_summary(packages_nt, packages_ng, packages_em, packages_cm, packages_all)


if __name__ == "__main__":
    main()
