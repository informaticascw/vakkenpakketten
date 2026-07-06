from itertools import combinations, product
from pathlib import Path
from typing import Dict, FrozenSet, List, Set
from pprint import pformat

#
# Data
#

# max 4 languages: packages from 5150 to 4910
# no "wisb" on cm: packages from 4910 to 4156
# wisb with wisc not allowed: # packages from 4156 to 3888
# wisb with wisa not allowed: # packages from 3888 to 3620

# nat bij ng met wisa
# ak bij ng met wisb
# ak in ema and emb
# no econ in cm (would create about 900 addtional packages)
# no biol in nt (would add 0 packages because this was already possible through an ntg-profile)

BASE_FILENAME: str = "vwo_8vakken_1vrij_allcombos_2mvtvrij_somemoreprofiles_somelimits"
PACKAGELIST_FILE: str = f"{BASE_FILENAME}_packages.txt"
REPORT_FILE: str = f"{BASE_FILENAME}_report.txt"

NUMBER_OF_SUBJECTS: int = 8
NUMBER_OF_FREE_CHOICE_SUBJECTS: int = 1
MAX_NUMBER_OF_LANGUAGES: int = 4 # packages from 5150 to 4910

ALL_SUBJECTS: Set[str] = {"ak", "beco", "biol", "chtc", "ct", "dutl", "econ", "entl", "fatl", "fi", "ges", "gtc", "in", "ltc", "mu", "nat", "netl", "schk", "sptl", "te", "wisa", "wisb", "wisc", "wisd"}

FORBIDDEN_PAIRS: List[Set[str]] = [

]

PROFILE_RULES: Dict[str, Dict[str, object]] = {
    "_common": {
        "common_groups": [{"netl"}, {"entl", "ct"}],
    },
    "nt": {
        "profile_groups": [
            ALL_SUBJECTS,
            {"nat"},
            {"schk"},
            {"wisb"},
            {"in", "wisd"}, # no # add biol
        ],
        "free_groups": [
            ALL_SUBJECTS,
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "ng": {
        "profile_groups": [
            ALL_SUBJECTS,
            {"ak","nat"}, # add nat
            {"biol"},
            {"schk"},
            {"wisa", "wisb"}, # add wisb
        ],
        "free_groups": [
            ALL_SUBJECTS,
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "ngt": {
        "profile_groups": [
            ALL_SUBJECTS,
            {"nat"},
            {"biol"},
            {"schk"},
            {"wisb"},
        ],
        "free_groups": [
            ALL_SUBJECTS,
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "ema": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"ges"},
            {"econ"},
            {"beco", "ak"}, # add "ak", no "fatl", "dutl","sptl","chtc"
            {"wisa"},
        ],
        "free_groups": [
            ALL_SUBJECTS,
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "emb": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"ges"},
            {"econ"},
            {"beco", "ak"}, # add "ak", no "fatl", "dutl","sptl","chtc"
            {"wisb"},
        ],
        "free_groups": [
            ALL_SUBJECTS,
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "cm": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"ges"},
            {"ak"}, # not add "econ"
            {"wisc", "wisa"}, # add "wisb" # packages from 4910 to 4156
            {"fi", "te", "mu", "fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
        ],
        "free_groups": [
            ALL_SUBJECTS,
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
}

#
# create package functions
#

def generate_subpakketten_gemeenschappelijk() -> List[Set[str]]:
    required_groups: List[Set[str]] = PROFILE_RULES["_common"]["common_groups"]

    # Combine all subjects from the first required group with all subjects
    # from the second required group, and so on until the last group.
    valid: Set[FrozenSet[str]] = set()

    for subject_choice in product(*required_groups):
        package = frozenset(subject_choice)

        # Keep exactly one subject per required group.
        if len(package) == len(required_groups):
            valid.add(package)

    return [set(package) for package in valid]


def generate_subpakketten_profiel(profile_name: str) -> List[Set[str]]:
    required_groups: List[Set[str]] = list(PROFILE_RULES[profile_name]["profile_groups"])

    # Combine all subjects from the first required group with all subjects
    # from the second required group, and so on until the last group.
    valid: Set[FrozenSet[str]] = set()

    for subject_choice in product(*required_groups):
        package = frozenset(subject_choice)

        # Keep exactly one subject per required group.
        if len(package) == len(required_groups):
            valid.add(package)

    return [set(package) for package in valid]


def generate_subpakketten_vrijekeuze(profile_name: str) -> List[Set[str]]:
    groups: List[Set[str]] = PROFILE_RULES[profile_name]["free_groups"]
    pick_k: int = PROFILE_RULES[profile_name]["free_pick_groups"]

    # Choose pick_k free-choice groups first, then combine one subject from
    # each chosen group.
    valid: Set[FrozenSet[str]] = set()

    for index_combo in combinations(range(len(groups)), pick_k):
        required_groups = [groups[idx] for idx in index_combo]

        for subject_choice in product(*required_groups):
            package = frozenset(subject_choice)

            # Keep exactly one subject per chosen group.
            if len(package) == len(required_groups):
                valid.add(package)

    return [set(package) for package in valid]

def combine_raw(
    common_subpackages: List[Set[str]],
    profile_subpackages: List[Set[str]],
    free_subpackages: List[Set[str]],
) -> Set[FrozenSet[str]]:
    # Combine only; rule filters are applied later in one global pass.
    result: Set[FrozenSet[str]] = set()

    for common_pkg in common_subpackages:
        for profile_pkg in profile_subpackages:
            for free_pkg in free_subpackages:
                combined = set()
                combined.update(common_pkg)
                combined.update(profile_pkg)
                combined.update(free_pkg)

                result.add(frozenset(combined))

    return result

#
# validation functions
#

def valid_wiskunde_rules(package: Set[str]) -> bool:
    # legal requirement
    if "wisd" in package and "wisb" not in package:
        return False

    # legal requirement
    if "wisc" in package and "wisa" in package:
        return False
        
    # school requirement # packages from 4156 to 3888
    if "wisc" in package and "wisb" in package:
       return False

    # school requirement # packages from 3888 to 3620
    if "wisa" in package and "wisb" in package:
       return False

    return True


def has_forbidden_school_combination(package: Set[str]) -> bool:
    # School-level forbidden subject pairs.
    for pair in FORBIDDEN_PAIRS:
        if pair.issubset(package):
            return True

    return False

def has_forbidden_entl_ct_combination(package: Set[str]) -> bool:
    # entl and ct are mutually exclusive in one package.
    return "entl" in package and "ct" in package

def has_over_x_languages(package: Set[str], max_nr_of_languages: int) -> bool:
    # Check if the package contains more than 4 language subjects.
    language_subjects = {"netl", "entl", "ct", "dutl", "fatl", "sptl", "chtc", "gtc", "ltc"}
    return len(package & language_subjects) > max_nr_of_languages

def has_valid_number_of_subjects(package: Set[str]) -> bool:
    # packages where the same subject has been chosen on multiple positions will have fewer than the required number of subjects.
    return len(package) == NUMBER_OF_SUBJECTS

#
# report functions
#

def write_output(packages_all: Set[FrozenSet[str]], output_file: str) -> None:
    lines = ["+".join(sorted(package)) for package in packages_all]
    Path(output_file).write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")


def write_report(report_text: str, report_file: str) -> None:
    Path(report_file).write_text(report_text + "\n", encoding="utf-8")


def main() -> None:

    #
    # create packages of subjects
    #

    common_subpackages = generate_subpakketten_gemeenschappelijk()

    packages_nt_raw = combine_raw(
        common_subpackages,
        generate_subpakketten_profiel("nt"),
        generate_subpakketten_vrijekeuze("nt"),
    )
    packages_ng_raw = combine_raw(
        common_subpackages,
        generate_subpakketten_profiel("ng"),
        generate_subpakketten_vrijekeuze("ng"),
    )
    packages_ngt_raw = combine_raw(
        common_subpackages,
        generate_subpakketten_profiel("ngt"),
        generate_subpakketten_vrijekeuze("ngt"),
    )
    packages_ema_raw = combine_raw(
        common_subpackages,
        generate_subpakketten_profiel("ema"),
        generate_subpakketten_vrijekeuze("ema"),
    )
    packages_emb_raw = combine_raw(
        common_subpackages,
        generate_subpakketten_profiel("emb"),
        generate_subpakketten_vrijekeuze("emb"),
    )
    packages_cm_raw = combine_raw(
        common_subpackages,
        generate_subpakketten_profiel("cm"),
        generate_subpakketten_vrijekeuze("cm"),
    )

    # Combine all raw profile packages first.
    packages_all_raw = (
        packages_nt_raw
        | packages_ng_raw
        | packages_ngt_raw
        | packages_ema_raw
        | packages_emb_raw
        | packages_cm_raw
    )

    #
    # remove packages that violate rules
    #

    # Apply global rules to a copy of the raw package set.
    packages_all = set(packages_all_raw)

    # Keep only combinations with correct number of subjects
    packages_all = {
        package for package in packages_all if has_valid_number_of_subjects(set(package))
    }
    # Apply school rules forbidding certain combinations
    packages_all = {
        package for package in packages_all if not has_forbidden_school_combination(set(package))
    }
    # Apply legal and school math rules.
    packages_all = {
        package for package in packages_all if valid_wiskunde_rules(set(package))
    }
    # Apply legal rules that ct and entl are not allowed in one package.
    packages_all = {
        package for package in packages_all if not has_forbidden_entl_ct_combination(set(package))
    }
     # Apply school max number of languages per package.
    packages_all = {
        package for package in packages_all if not has_over_x_languages(set(package),MAX_NUMBER_OF_LANGUAGES)
    }

    #
    # create report and output files
    #

    # Profile-specific counts after global filtering.
    report_lines_part1 = [
        f"BASEFILENAME: {BASE_FILENAME}",
        "",
        f"NUMBER_OF_SUBJECTS: {NUMBER_OF_SUBJECTS}",
        f"NUMBER_OF_FREE_CHOICE_SUBJECTS: {NUMBER_OF_FREE_CHOICE_SUBJECTS}",
        "",
        "PACKAGE COUNTS:",
        f"- nt packages: {len(packages_all & packages_nt_raw)}",
        f"- ng packages: {len(packages_all & packages_ng_raw)}",
        f"- ngt packages: {len(packages_all & packages_ngt_raw)}",
        f"- ema packages: {len(packages_all & packages_ema_raw)}",
        f"- emb packages: {len(packages_all & packages_emb_raw)}",
        f"- cm packages: {len(packages_all & packages_cm_raw)}",
        f"all unique packages: {len(packages_all)}",
        "",
    ]
    report_lines_part2 = [
        "FORBIDDEN_PAIRS:",
        pformat(FORBIDDEN_PAIRS, width=100, sort_dicts=False),
        "PROFILE_RULES:",
        pformat(PROFILE_RULES, width=100, sort_dicts=False),
    ]

    screen_text = "\n".join(report_lines_part1)
    print(screen_text)
  
    report_text = "\n".join(report_lines_part1 + report_lines_part2)
    write_report(report_text, REPORT_FILE)
    print(f"REPORT_FILE: {REPORT_FILE}")

    write_output(packages_all, PACKAGELIST_FILE)
    print(f"PACKAGELIST_FILE: {PACKAGELIST_FILE}")

if __name__ == "__main__":
    main()
