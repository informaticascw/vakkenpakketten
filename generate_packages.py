from itertools import combinations, product
from pathlib import Path
from typing import Dict, FrozenSet, List, Set
from pprint import pformat

BASE_FILENAME: str = "VWO_packages_2526_9vakken"
PACKAGELIST_FILE: str = f"{BASE_FILENAME}_packages.txt"
REPORT_FILE: str = f"{BASE_FILENAME}_report.txt"

NUMBER_OF_SUBJECTS: int = 9
NUMBER_OF_FREE_CHOICE_SUBJECTS: int = 2

ALL_SUBJECTS: Set[str] = {"ak", "beco", "biol", "chtc", "ct", "dutl", "econ", "entl", "fatl", "fi", "ges", "gtc", "in", "ltc", "mu", "nat", "netl", "schk", "sptl", "te", "wisa", "wisb", "wisc", "wisd"}

FORBIDDEN_PAIRS: List[Set[str]] = [
    {"te", "mu"},
    {"in", "mu"},
    {"in", "fi"},
    {"wisd", "fi"},
    {"wisd", "te"},
    {"wisd", "mu"},
    {"in", "ak"},
]

PROFILE_RULES: Dict[str, Dict[str, object]] = {
    "_common": {
        "common_groups": [{"netl"}, {"entl", "ct"}],
    },
    "nt": {
        "profile_groups": [
            {"fatl", "dutl", "gtc", "ltc"},
            {"nat"},
            {"schk"},
            {"wisb"},
            {"in", "wisd"},
        ],
        "free_groups": [
            {"econ", "beco"},
            {"ak", "in"},
            {"te"},
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "ng": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"ak"},
            {"biol"},
            {"schk"},
            {"wisa"},
        ],
        "free_groups": [
            {"sptl", "fatl", "dutl", "chtc"},
            {"econ", "beco"},
            {"fi", "mu", "te"},
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "ngt": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"nat"},
            {"biol"},
            {"schk"},
            {"wisb"},
        ],
        "free_groups": [
            {"sptl", "fatl", "dutl", "chtc"},
            {"in", "wisd"},
            {"econ", "beco"},
            {"fi", "mu", "te"},
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "ema": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"ges"},
            {"econ"},
            {"beco"},
            {"wisa"},
        ],
        "free_groups": [
            {"sptl", "fatl", "dutl", "chtc"},
            {"ak"},
            {"fi"},
            {"mu", "te"},
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "emb": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"ges"},
            {"econ"},
            {"beco"},
            {"wisb"},
        ],
        "free_groups": [
            {"nat"},
            {"ak", "in"},
            {"fi", "mu", "te"},
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
    "cm": {
        "profile_groups": [
            {"fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
            {"ges"},
            {"ak"},
            {"wisc", "wisa"},
            {"fi", "te", "mu", "fatl", "dutl", "sptl", "chtc", "gtc", "ltc"},
        ],
        "free_groups": [
            {"sptl", "fatl", "dutl", "chtc"},
            {"econ", "beco"},
            {"fi"},
            {"mu", "te"},
        ],
        "free_pick_groups": NUMBER_OF_FREE_CHOICE_SUBJECTS,
    },
}


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


def valid_wiskunde_rules(package: Set[str]) -> bool:
    # Math consistency rules.
    if "wisd" in package and "wisb" not in package:
        return False

    if "wisc" in package and "wisa" in package:
        return False

    return True


def has_forbidden_school_combination(package: Set[str]) -> bool:
    # School-level forbidden subject pairs.
    for pair in FORBIDDEN_PAIRS:
        if pair.issubset(package):
            return True

    return False


def has_valid_number_of_subjects(package: Set[str]) -> bool:
    return len(package) == NUMBER_OF_SUBJECTS


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


def write_output(packages_all: Set[FrozenSet[str]], output_file: str) -> None:
    lines = ["+".join(sorted(package)) for package in packages_all]
    Path(output_file).write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")


def write_report(report_text: str, report_file: str) -> None:
    Path(report_file).write_text(report_text + "\n", encoding="utf-8")


def main() -> None:
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

    # Apply global rules to a copy of the raw package set.
    packages_all = set(packages_all_raw)

    # Keep only combinations with correct number of subjects
    packages_all = {
        package for package in packages_all if has_valid_number_of_subjects(set(package))
    }
    # Apply school rules.
    packages_all = {
        package for package in packages_all if not has_forbidden_school_combination(set(package))
    }
    # Apply math rules.
    packages_all = {
        package for package in packages_all if valid_wiskunde_rules(set(package))
    }

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
