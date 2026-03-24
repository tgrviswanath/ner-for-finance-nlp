"""
Finance NER service using spaCy + custom EntityRuler patterns.
Lazy-loads the spaCy model and adds finance-specific patterns on first use.
"""
import spacy
from app.core.entities import ENTITY_META, FINANCE_PATTERNS
from app.core.config import settings

_nlp = None

# Finance-relevant spaCy labels to keep
KEEP_LABELS = set(ENTITY_META.keys())


def _load():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(settings.SPACY_MODEL)
        # Add finance EntityRuler before the NER component
        ruler = _nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": False})
        ruler.add_patterns(FINANCE_PATTERNS)


def extract_entities(text: str) -> dict:
    _load()
    doc = _nlp(text)

    entities = []
    seen = set()
    for ent in doc.ents:
        if ent.label_ not in KEEP_LABELS:
            continue
        key = (ent.text.strip(), ent.label_)
        if key in seen:
            continue
        seen.add(key)
        meta = ENTITY_META.get(ent.label_, {})
        entities.append({
            "text":  ent.text.strip(),
            "label": ent.label_,
            "label_name": meta.get("label", ent.label_),
            "color": meta.get("color", "#607d8b"),
            "icon":  meta.get("icon", "🔖"),
            "start": ent.start_char,
            "end":   ent.end_char,
        })

    # Group by label for summary
    by_label: dict[str, list[str]] = {}
    for ent in entities:
        by_label.setdefault(ent["label"], []).append(ent["text"])

    # Build label counts for chart
    label_counts = [
        {
            "label": k,
            "label_name": ENTITY_META.get(k, {}).get("label", k),
            "count": len(v),
            "color": ENTITY_META.get(k, {}).get("color", "#607d8b"),
        }
        for k, v in by_label.items()
    ]

    return {
        "entities": entities,
        "by_label": by_label,
        "label_counts": label_counts,
        "total": len(entities),
        "word_count": len(text.split()),
    }
