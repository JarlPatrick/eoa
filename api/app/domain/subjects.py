from __future__ import annotations

from enum import StrEnum

# NOTE: This map is intentionally hardcoded (as requested). If a new subject is added
# to the DB, update this mapping.
SUBJECT_ABBREV: dict[str, str] = {
    "Füüsika": "efo",
    "Keemia": "eko",
    "Informaatika": "eio",
    "Bioloogia": "ebo",
    "Loodusteadused": "elo",
    "Matemaatika": "emo",
    "Astronoomia": "ast",
    "Filosoofia": "fil",
    "Maateadused": "mte",
    "Lingvistika": "lin",
    "Usundiõpetus": "usu",
    "Emakeel": "ema",
    "Inglise keel": "ing",
    "Saksa keel": "sak",
    "Vene keel emakeelena": "vem",
    "Vene keel võõrkeelena": "vvk",
    "Prantsuse keel": "pra",
    "Geograafia": "geo",
    "Inimeseõpetus": "ini",
}

SUBJECT_BY_ABBREV: dict[str, str] = {
    abbrev: name for name, abbrev in SUBJECT_ABBREV.items()
}
if len(SUBJECT_BY_ABBREV) != len(SUBJECT_ABBREV):
    raise RuntimeError("Duplicate subject abbreviations in SUBJECT_ABBREV")


class SubjectAbbrev(StrEnum):
    efo = "efo"
    eko = "eko"
    eio = "eio"
    ebo = "ebo"
    elo = "elo"
    emo = "emo"
    ast = "ast"
    fil = "fil"
    mte = "mte"
    lin = "lin"
    usu = "usu"
    ema = "ema"
    ing = "ing"
    sak = "sak"
    vem = "vem"
    vvk = "vvk"
    pra = "pra"
    geo = "geo"
    ini = "ini"
