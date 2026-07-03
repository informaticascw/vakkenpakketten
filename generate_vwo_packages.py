from itertools import combinations, product
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

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

COMMON_REQUIRED: Set[str] = {"netl", "entl"}
ONE_COMMON_LANGUAGE_REQUIRED: Set[str] = {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"}

FORBIDDEN_PAIRS: Set[frozenset[str]] = {
    frozenset(("te", "mu")),
    frozenset(("in", "mu")),
    frozenset(("in", "fi")),
    frozenset(("wisd", "fi")),
    frozenset(("wisd", "te")),
    frozenset(("wisd", "mu")),
    frozenset(("in", "ak")),
}

# Legal math combinations based on the VWO free-part rules.
# Allowed pairs: (A, B) and (B, C). Any package with D must include B.
def valid_math_combination(package: Set[str]) -> bool:
    if "wisd" in package and "wisb" not in package:
        return False

    has_a = "wisa" in package
    has_b = "wisb" in package
    has_c = "wisc" in package

    # Not allowed as a direct A+C combination.
    if has_a and has_c and not has_b:
        return False

    return True


def has_forbidden_pair(package: Set[str]) -> bool:
    return any(pair.issubset(package) for pair in FORBIDDEN_PAIRS)


def valid_nt_language_rule(package: Set[str]) -> bool:
    # School rule interpreted as: in NT, modern language choice is only French or German.
    modern_languages = {"fatl", "dutl", "sptl", "chtc"}
    selected_modern_languages = package.intersection(modern_languages)
    return selected_modern_languages.issubset({"fatl", "dutl"})


def valid_common_requirements(package: Set[str]) -> bool:
    if "netl" not in package:
        return False

    if not package.intersection({"entl", "ct"}):
        return False

    if not package.intersection(ONE_COMMON_LANGUAGE_REQUIRED):
        return False

    if has_forbidden_pair(package):
        return False

    if not valid_math_combination(package):
        return False

    return True


PROFILE_RULES: Dict[str, Dict[str, Iterable[Set[str]]]] = {
    "nt": {
        "required_all": {"wisb", "nat", "schk"},
        "required_one_of": [
            {"in", "wisd"},
        ],
    },
    "ng": {
        "required_all": {"wisa", "biol", "schk", "ak"},
        "required_one_of": [],
    },
    "em": {
        "required_all": {"ges", "econ", "beco"},
        "required_one_of": [
            {"wisa", "wisb"},
        ],
    },
    "cm": {
        "required_all": {"ges", "ak"},
        "required_one_of": [
            {"wisc", "wisa"},
            {"fi", "te", "mu", "fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
        ],
    },
}


def valid_free_part_requirements(profile: str, package: Set[str]) -> bool:
    # Lessentabel VWO: vrije deel (2) interpreted as exactly two chosen subjects
    # from the profile-specific vrije-deel options.
    if profile == "cm":
        free_pool = {"sptl", "fatl", "dutl", "chtc", "econ", "beco", "fi", "mu", "te"}
        return len(package.intersection(free_pool)) == 2

    if profile == "em":
        if "wisa" in package:
            free_pool = {"sptl", "fatl", "dutl", "chtc", "ak", "fi", "mu", "te"}
        elif "wisb" in package:
            free_pool = {"nat", "ak", "in", "fi", "mu", "te"}
        else:
            return False
        return len(package.intersection(free_pool)) == 2

    if profile == "ng":
        free_pool = {"sptl", "fatl", "dutl", "chtc", "econ", "beco", "fi", "mu", "te"}
        return len(package.intersection(free_pool)) == 2

    if profile == "nt":
        free_pool = {"econ", "beco", "ak", "in", "te"}
        return len(package.intersection(free_pool)) == 2

    return True


def package_is_valid(profile: str, package: Set[str]) -> bool:
    if len(package) not in PACKAGE_SIZES:
        return False

    if not valid_common_requirements(package):
        return False

    if profile == "nt" and not valid_nt_language_rule(package):
        return False

    rules = PROFILE_RULES[profile]
    required_all = set(rules["required_all"])
    if not required_all.issubset(package):
        return False

    for options in rules["required_one_of"]:
        if not set(options).intersection(package):
            return False

    if not valid_free_part_requirements(profile, package):
        return False

    return True


def generate_for_profile(profile: str) -> Set[str]:
    rules = PROFILE_RULES[profile]
    required_all = set(rules["required_all"])
    required_groups = [set(group) for group in rules["required_one_of"]]

    results: Set[str] = set()

    # Build minimal base sets from all profile-choice combinations.
    for choices in product(*required_groups):
        base = {"netl"} | required_all | set(choices)

        if len(base) > max(PACKAGE_SIZES):
            continue

        if not base.intersection(ONE_COMMON_LANGUAGE_REQUIRED):
            # If no common language in base, it can still be added later.
            pass

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


def generate_all_packages() -> Dict[str, Set[str]]:
    by_profile: Dict[str, Set[str]] = {}
    for profile in PROFILE_RULES:
        by_profile[profile] = generate_for_profile(profile)
    return by_profile


def write_output(by_profile: Dict[str, Set[str]], path: Path) -> None:
    # Final output is one package per line, no profile label, unique across profiles.
    all_packages = sorted(set().union(*by_profile.values()))
    path.write_text("\n".join(all_packages) + "\n", encoding="utf-8")


def print_summary(by_profile: Dict[str, Set[str]]) -> None:
    total_unique = len(set().union(*by_profile.values()))
    print("Generated VWO package counts:")
    for profile, packages in by_profile.items():
        print(f"- {profile}: {len(packages)}")
    print(f"- total unique packages: {total_unique}")
    print(f"Output file: {OUTPUT_FILE}")


def main() -> None:
    by_profile = generate_all_packages()
    write_output(by_profile, OUTPUT_FILE)
    print_summary(by_profile)


if __name__ == "__main__":
    main()
