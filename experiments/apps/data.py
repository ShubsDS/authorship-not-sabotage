"""Build the monitor-evaluation sample set from the anchor paper's public dataset.

Source: huggingface.co/datasets/eugenekoran/apps-control-arena-high-quality, the dataset
released with 2605.15377. One sample = one Python program plus a ground-truth label
(1 = backdoored/attack, 0 = honest).

Split semantics were reverse-engineered from the dataset and cross-checked against the
counts stated in the paper (sec 4.1); see `build_samples` for the reconstruction and
`SPLIT_DEVIATION` for the one place we could not recover their exact choice.
"""

from __future__ import annotations

import hashlib
import io
import tokenize
from dataclasses import dataclass, asdict

DATASET_ID = "eugenekoran/apps-control-arena-high-quality"

# Paper sec 4.1, verified against the downloaded dataset on 2026-08-07.
EXPECTED = {
    "test_attack": 172,
    "test_honest": 1203,
    "trainval_total": 2418,
    "train_total": 1936,
    "val_total": 482,
}

SPLIT_DEVIATION = (
    "The paper reports 1936 train / 482 validation samples but does not publish the "
    "assignment. We take the 241 train problems with the smallest SHA1(problem_id) as "
    "validation, which reproduces the stated sample counts exactly (968*2=1936, "
    "241*2=482) but not necessarily their exact membership. Since train/val are used "
    "only to fit monitor thresholds and never to compute a headline number, membership "
    "differences cannot affect the reported test results. Test is taken verbatim from "
    "the dataset's own test split and IS exact (172 attack / 1203 honest)."
)


@dataclass(frozen=True)
class Sample:
    """One program shown to a monitor."""

    sample_id: str
    problem_id: str
    code: str
    label: int  # 1 = attack (backdoored), 0 = honest
    split: str  # train | val | test
    attacker_model: str | None  # None for honest samples
    question: str  # the problem statement; the monitor needs it to judge task-relevance


def strip_comments(code: str) -> str:
    """Remove Python comments while preserving all other formatting.

    Port of scripts/comment_stripper.py from the anchor's repo
    (github.com/Multi-Signal-Control-SPAR/Multi-Signal-Monitoring), including its
    behaviour of dropping lines that become empty once the comment is removed.

    This is mandatory preprocessing, not a nicety: the paper found that backdoor code in
    this dataset frequently carries comments that name the backdoor outright, which leaks
    the label to any monitor that reads them (sec 4.1).
    """
    lines = code.split("\n")
    comment_positions: dict[int, int] = {}
    try:
        readline = io.BytesIO(code.encode("utf-8")).readline
        for token in tokenize.tokenize(readline):
            if token.type == tokenize.COMMENT:
                line = token.start[0] - 1  # tokenize is 1-based
                comment_positions.setdefault(line, token.start[1])
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # Malformed source: return it untouched rather than silently mangling it.
        return code

    out = []
    for i, line in enumerate(lines):
        if i in comment_positions:
            cleaned = line[: comment_positions[i]].rstrip()
            if cleaned:
                out.append(cleaned)
        else:
            out.append(line)
    return "\n".join(out)


def _pick_backdoor(row: dict) -> dict | None:
    """The backdoor variant the dataset designates for this problem.

    Rows carry up to 25 candidate backdoors from different attacker models; the dataset's
    `top_backdoor_model` field names the chosen one. We require it to both work (exploits
    the secret input) and pass the public tests, which is the paper's filter for a usable
    attack.
    """
    top = row.get("top_backdoor_model")
    usable = [b for b in row["backdoors"] if b["backdoor_works"] and b["passes_tests"]]
    if not usable:
        return None
    if top:
        for b in usable:
            if b["model"] == top:
                return b
    return usable[0]


def _honest_code(row: dict) -> str | None:
    for s in row["solutions"]:
        if s["passes_tests"] and s["compiles"]:
            return s["code"]
    return None


N_VAL_PROBLEMS = 241  # 241*2 = 482 validation samples, the count stated in the paper


def _hash_rank(problem_id: str) -> int:
    return int.from_bytes(hashlib.sha1(str(problem_id).encode()).digest()[:8], "big")


def _val_problem_ids(problem_ids: list[str], n_val: int = N_VAL_PROBLEMS) -> frozenset[str]:
    """The n_val problems with the smallest hash. Deterministic and order-independent.

    A hash *threshold* cannot hit an exact count, so we rank instead: this reproduces the
    paper's 1936/482 sample counts exactly while staying reproducible from problem_id
    alone. Membership still differs from theirs; see SPLIT_DEVIATION.
    """
    return frozenset(sorted(problem_ids, key=_hash_rank)[:n_val])


def build_samples(dataset, strip: bool = True) -> list[Sample]:
    """Reconstruct the monitor-evaluation samples from the raw dataset.

    test: one sample per row. Rows whose designated backdoor works become attack samples
    carrying the backdoor code; the rest become honest samples carrying the reference
    solution. This reproduces the paper's 172 attack / 1203 honest exactly.

    train+val: each of the 1209 fully-backdoored problems yields BOTH an attack and an
    honest sample, giving the paper's 2418 (50% attack) before the 80/20 split.
    """
    samples: list[Sample] = []

    for row in dataset["test"]:
        pid = str(row["problem_id"])
        if row["backdoor_works"]:
            bd = _pick_backdoor(row)
            if bd is None:
                continue
            code = bd["backdoor_code"]
            samples.append(
                Sample(f"test/{pid}/attack", pid, strip_comments(code) if strip else code, 1, "test", bd["model"], row["question"])
            )
        else:
            code = _honest_code(row)
            if code is None:
                continue
            samples.append(
                Sample(f"test/{pid}/honest", pid, strip_comments(code) if strip else code, 0, "test", None, row["question"])
            )

    usable_train = [r for r in dataset["train"] if _pick_backdoor(r) and _honest_code(r)]
    val_ids = _val_problem_ids([str(r["problem_id"]) for r in usable_train])

    for row in usable_train:
        pid = str(row["problem_id"])
        bd = _pick_backdoor(row)
        honest = _honest_code(row)
        split = "val" if pid in val_ids else "train"
        samples.append(
            Sample(
                f"{split}/{pid}/attack",
                pid,
                strip_comments(bd["backdoor_code"]) if strip else bd["backdoor_code"],
                1,
                split,
                bd["model"],
                row["question"],
            )
        )
        samples.append(
            Sample(f"{split}/{pid}/honest", pid, strip_comments(honest) if strip else honest, 0, split, None, row["question"])
        )

    return samples


def manifest(samples: list[Sample]) -> dict:
    """Counts to check against EXPECTED before any monitor is run."""
    by = lambda sp, lb: sum(1 for s in samples if s.split == sp and s.label == lb)  # noqa: E731
    attackers: dict[str, int] = {}
    for s in samples:
        if s.attacker_model:
            attackers[s.attacker_model] = attackers.get(s.attacker_model, 0) + 1

    m = {
        "dataset_id": DATASET_ID,
        "n_total": len(samples),
        "n_attack": sum(1 for s in samples if s.label == 1),
        "n_honest": sum(1 for s in samples if s.label == 0),
        "test_attack": by("test", 1),
        "test_honest": by("test", 0),
        "train_total": by("train", 0) + by("train", 1),
        "val_total": by("val", 0) + by("val", 1),
        "trainval_total": sum(1 for s in samples if s.split in ("train", "val")),
        "test_attacker_models": attackers,
        "split_deviation": SPLIT_DEVIATION,
    }
    m["matches_paper"] = {k: m[k] == v for k, v in EXPECTED.items()}
    return m


def sample_to_dict(s: Sample) -> dict:
    return asdict(s)
