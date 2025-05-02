from .csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex

# TODO: This should all be user configs
# TODO: This should be user customizable from the .tshconfig

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
RIGHT_K = "\x1b[C"
LEFT_K = "\x1b[D"
BACK_K = ("\x7f", "\b")
ADD_ITEM_ACTION = ["a", "add"]
EXIT_PROG_ACTION = ["e", "exit"]
