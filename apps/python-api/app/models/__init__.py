"""
Model data re-exports for backward compatibility with migrated services.
"""
from app.models.box_models import (
    BOX_MODELS_DATA,
    EJC_BOX_MODELS_DATA,
    COMPONENTS,
    HOLE_SIZES,
    SALT_MALZEME_COMPONENTS,
    EJC_MIN_EDGE_MARGIN,
    EJC_MIN_HOLE_CLEARANCE,
    get_all_box_models,
    get_box_model_by_id,
    get_all_ejc_box_models,
    get_ejc_box_model_by_id,
    get_hole_rules,
    get_component,
)
from app.models.switchgear import (
    SWITCHGEAR_CATALOG,
    get_all_switchgear,
    get_switchgear_by_id,
    get_switchgear_by_category,
)
from app.models.cover_elements import (
    COVER_ELEMENTS_CATALOG,
    get_all_cover_elements,
    get_cover_element_by_id,
    get_cover_elements_by_category,
)

__all__ = [
    "BOX_MODELS_DATA",
    "EJC_BOX_MODELS_DATA",
    "COMPONENTS",
    "HOLE_SIZES",
    "SALT_MALZEME_COMPONENTS",
    "get_all_box_models",
    "get_box_model_by_id",
    "get_all_ejc_box_models",
    "get_ejc_box_model_by_id",
    "get_hole_rules",
    "get_component",
    "EJC_MIN_EDGE_MARGIN",
    "EJC_MIN_HOLE_CLEARANCE",
    "SWITCHGEAR_CATALOG",
    "get_all_switchgear",
    "get_switchgear_by_id",
    "get_switchgear_by_category",
    "COVER_ELEMENTS_CATALOG",
    "get_all_cover_elements",
    "get_cover_element_by_id",
    "get_cover_elements_by_category",
]
