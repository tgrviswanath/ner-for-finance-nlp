"""
Finance-specific entity labels and their display metadata.
Used by both the rule-based extractor and the UI.
"""

# Entity label → display info
ENTITY_META = {
    # spaCy built-in labels (finance-relevant)
    "ORG":      {"label": "Organization",   "color": "#1976d2", "icon": "🏢"},
    "PERSON":   {"label": "Person",         "color": "#7b1fa2", "icon": "👤"},
    "GPE":      {"label": "Location",       "color": "#388e3c", "icon": "📍"},
    "DATE":     {"label": "Date",           "color": "#f57c00", "icon": "📅"},
    "MONEY":    {"label": "Money",          "color": "#c62828", "icon": "💰"},
    "PERCENT":  {"label": "Percentage",     "color": "#00838f", "icon": "📊"},
    "CARDINAL": {"label": "Number",         "color": "#5d4037", "icon": "🔢"},
    "PRODUCT":  {"label": "Product",        "color": "#558b2f", "icon": "📦"},
    "EVENT":    {"label": "Event",          "color": "#ad1457", "icon": "📌"},
    "LAW":      {"label": "Law/Regulation", "color": "#4527a0", "icon": "⚖️"},
    # Custom finance labels (added via EntityRuler)
    "TICKER":   {"label": "Stock Ticker",   "color": "#0277bd", "icon": "📈"},
    "METRIC":   {"label": "Finance Metric", "color": "#2e7d32", "icon": "📉"},
    "QUARTER":  {"label": "Fiscal Quarter", "color": "#e65100", "icon": "🗓️"},
}

# Finance-specific patterns for EntityRuler
FINANCE_PATTERNS = [
    # Stock tickers: AAPL, MSFT, GOOGL, TSLA, etc.
    {"label": "TICKER", "pattern": [{"TEXT": {"REGEX": r"^[A-Z]{1,5}$"}},]},
    # Common finance metrics
    {"label": "METRIC", "pattern": [{"LOWER": "revenue"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "ebitda"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "eps"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "p/e"}, {"LOWER": "ratio"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "net"}, {"LOWER": "income"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "gross"}, {"LOWER": "margin"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "market"}, {"LOWER": "cap"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "market"}, {"LOWER": "capitalization"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "earnings"}, {"LOWER": "per"}, {"LOWER": "share"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "return"}, {"LOWER": "on"}, {"LOWER": "equity"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "free"}, {"LOWER": "cash"}, {"LOWER": "flow"}]},
    {"label": "METRIC", "pattern": [{"LOWER": "operating"}, {"LOWER": "income"}]},
    # Fiscal quarters
    {"label": "QUARTER", "pattern": [{"TEXT": {"REGEX": r"^Q[1-4]$"}}, {"TEXT": {"REGEX": r"^\d{4}$"}}]},
    {"label": "QUARTER", "pattern": [{"LOWER": {"IN": ["q1", "q2", "q3", "q4"]}}, {"TEXT": {"REGEX": r"^\d{4}$"}}]},
    {"label": "QUARTER", "pattern": [{"LOWER": "first"}, {"LOWER": "quarter"}]},
    {"label": "QUARTER", "pattern": [{"LOWER": "second"}, {"LOWER": "quarter"}]},
    {"label": "QUARTER", "pattern": [{"LOWER": "third"}, {"LOWER": "quarter"}]},
    {"label": "QUARTER", "pattern": [{"LOWER": "fourth"}, {"LOWER": "quarter"}]},
]
