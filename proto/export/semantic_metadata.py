# Semantic measurement metadata — extracted from proto/static/js/semantic-meta.js

AREA_SEMANTIC_TAGS = {
    "gross_floor_area", "floor_area", "use_area",
}

SEMANTIC_PROFILE_MAP = {
    "site_land_area":      "site_land_area",
    "site_boundary":       "site_boundary",
    "building_footprint":  "building_footprint",
    "gross_floor_area":    "legal_building_area",
    "floor_area":          "use_area",
    "use_area":            "use_area",
    "parking_area":        "parking_area",
    "deduction_opening":   "deduction_area",
    "void":                "deduction_area",
    "legal_open_space":    "legal_open_space",
    "setback_measure_line":"setback_measure_line",
    "dimension_line":      "dimension_line",
    "reference_line":      "reference_line",
    "road_line":           "reference_line",
    "frontage_line":       "reference_line",
    "scale_line":          "scale_line",
    "north_arrow":         "north_arrow",
    "review_note":         "review_note",
    "label":               "label",
}

SEMANTIC_CATEGORY_MAP = {
    "site_land_area":      "site_fact",
    "site_boundary":       "site_fact",
    "building_footprint":  "site_fact",
    "gross_floor_area":    "area",
    "floor_area":          "area",
    "use_area":            "area",
    "parking_area":        "area",
    "deduction_opening":   "deduction",
    "void":                "deduction",
    "legal_open_space":    "site_fact",
    "setback_measure_line":"dimension",
    "dimension_line":      "dimension",
    "reference_line":      "reference",
    "road_line":           "reference",
    "frontage_line":       "reference",
    "scale_line":          "reference",
    "north_arrow":         "orientation",
    "review_note":         "annotation",
    "label":               "annotation",
}

SEMANTIC_REPORT_TARGET_MAP = {
    "site_land_area":      "Site Facts",
    "site_boundary":       "Site Facts",
    "building_footprint":  "Site Facts",
    "gross_floor_area":    "Building Area Summary",
    "floor_area":          "Building Area Summary",
    "use_area":            "Use Category Summary",
    "parking_area":        "Parking Summary",
    "deduction_opening":   "Deduction Summary",
    "void":                "Deduction Summary",
    "legal_open_space":    "Open Space Summary",
    "setback_measure_line":"Distance Facts",
    "dimension_line":      "Distance Facts",
    "reference_line":      "Audit Log",
    "road_line":           "Site Facts",
    "frontage_line":       "Site Facts",
    "scale_line":          "Audit Log",
    "north_arrow":         "Site Facts",
    "review_note":         "Audit Log",
    "label":               "Audit Log",
}

SEMANTIC_LAW_BASIS_MAP = {
    "gross_floor_area": "พื้นที่อาคาร",
    "floor_area":       "พื้นที่ใช้สอย",
    "legal_open_space": "ที่ว่าง",
    "site_land_area":   "ที่ดิน",
}

SEMANTIC_COUNTING_RULE_MAP = {
    "site_land_area":      "included",
    "site_boundary":       "reference",
    "building_footprint":  "reference",
    "gross_floor_area":    "included",
    "floor_area":          "included",
    "use_area":            "classified",
    "parking_area":        "classified",
    "deduction_opening":   "deducted",
    "void":                "deducted",
    "legal_open_space":    "included",
    "setback_measure_line":"reference",
    "dimension_line":      "reference",
    "reference_line":      "reference",
    "road_line":           "reference",
    "frontage_line":       "reference",
    "scale_line":          "reference",
    "north_arrow":         "reference",
    "review_note":         "reference",
    "label":               "reference",
}


def _derive_measurement_meta(tag: str) -> dict:
    return {
        "measurementProfile": SEMANTIC_PROFILE_MAP.get(tag, "review_note"),
        "objectCategory":     SEMANTIC_CATEGORY_MAP.get(tag, "annotation"),
        "reportTarget":       SEMANTIC_REPORT_TARGET_MAP.get(tag, "Audit Log"),
        "lawBasis":           SEMANTIC_LAW_BASIS_MAP.get(tag),
        "countingRule":       SEMANTIC_COUNTING_RULE_MAP.get(tag, "reference"),
    }


def _get_meta(obj: dict | None, semantic_tag: str) -> dict:
    obj = obj or {}
    return {
        "measurementProfile": obj.get("measurementProfile") or SEMANTIC_PROFILE_MAP.get(semantic_tag, "review_note"),
        "objectCategory":     obj.get("objectCategory")     or SEMANTIC_CATEGORY_MAP.get(semantic_tag, "annotation"),
        "reportTarget":       obj.get("reportTarget")       or SEMANTIC_REPORT_TARGET_MAP.get(semantic_tag, "Audit Log"),
        "lawBasis":           obj.get("lawBasis")           or SEMANTIC_LAW_BASIS_MAP.get(semantic_tag),
        "countingRule":       obj.get("countingRule")       or SEMANTIC_COUNTING_RULE_MAP.get(semantic_tag, "reference"),
    }
