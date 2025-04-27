from .csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex

# TODO: This should all be user configs

PAGER_TOP = "...\U00002B06 ..."
PAGER_BOTTOM = "...\U00002B07..."
ENTER = (
    "Press "
    + csl_str_factory("ENTER", CslStrStyleAttribute.BOLD, ColorIndex(9))
    + " to confirm."
)
UP_K = "\x1b[A"
DOWN_K = "\x1b[B"
ENTER_K = ["\r", "\n"]
