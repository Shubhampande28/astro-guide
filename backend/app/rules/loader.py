"""Loads and validates YAML rule files from rules_data/."""

from functools import lru_cache
from pathlib import Path

import yaml

from app.rules.dsl import DslError, parse
from app.rules.schema import Rule, RuleEffect, RuleSource

RULES_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "rules_data"


class RuleLoadError(Exception):
    pass


def _parse_rule(raw: dict) -> Rule:
    try:
        rule = Rule(
            id=raw["id"],
            topic=raw["topic"],
            condition=raw["condition"],
            weight=raw["weight"],
            effect=RuleEffect(**raw["effect"]),
            source=RuleSource(**raw["source"]),
            remedies=raw.get("remedies", []),
            status=raw.get("status", "draft"),
        )
    except (KeyError, TypeError) as e:
        raise RuleLoadError(f"Malformed rule {raw.get('id', '?')}: {e}") from e

    try:
        parse(rule.condition)
    except DslError as e:
        raise RuleLoadError(f"{rule.id}: invalid condition '{rule.condition}': {e}") from e

    return rule


def load_rules_from_file(path: Path) -> list[Rule]:
    with open(path, encoding="utf-8") as f:
        raw_list = yaml.safe_load(f) or []
    return [_parse_rule(raw) for raw in raw_list]


@lru_cache
def load_all_rules() -> tuple[Rule, ...]:
    rules: list[Rule] = []
    seen_ids: set[str] = set()
    for path in sorted(RULES_DATA_DIR.glob("*.yaml")):
        for rule in load_rules_from_file(path):
            if rule.id in seen_ids:
                raise RuleLoadError(f"Duplicate rule id: {rule.id}")
            seen_ids.add(rule.id)
            rules.append(rule)
    return tuple(rules)
