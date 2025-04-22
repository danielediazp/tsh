from enum import auto, StrEnum
from dataclasses import dataclass

from exceptions import NotSupportedStyleAttribute, InvalidColorIndex


class CslStrStyleAttribute(StrEnum):
    """
    An enum use to represent the Style Attributes supported by the `rich.console`
    object. These are the different formats support throughout the project for program
    output.
    """

    BOLD = auto()
    BLINK = auto()
    ITALIC = auto()
    REVERSE = auto()
    STRIKE = auto()
    UNDERLINE = auto()
    UNDERLINE2 = auto()
    FRAME = auto()
    ENCIRCLE = auto()
    OVERLINE = auto()


@dataclass(frozen=True)
class ColorIndex:
    """Constant Class used to define colors that can be printed in the `rich.console`.
    The library supports any x if 1 <= x <= 255.

    Raises:
        InvalidColorIndex: If the val to Initialize the object is not 1 <= val <= 255

    Defines:
        __str__
    """

    val: int

    def __post_init__(self):
        if not (1 <= self.val <= 255):
            raise InvalidColorIndex

    def __str__(self):
        return f"color({self.val})"


def csl_str_factory(
    text: str,
    style_attr: CslStrStyleAttribute | list[CslStrStyleAttribute] = None,
    color: ColorIndex = None,
) -> str:
    """
    Creates a formatted `rich.console` string

    Args:
        text (str): the text to apply the format to
        style_attr (CslStrStyleAttribute | list[CslStrStyleAttribute]): the format that will be apply to the text

    Returns:
        str: in the format `[style_attr] text [/style_attr]`

    Raises:
        NotSupportedStyleAttribute: if `style_attr` is not supported by the `CslStrStyleAttribute` enum

    Example:
        >>> csl_str_factory("Hello", CslStrStyleAttribute.BOLD)
        >>> "[bold]Hello[/bold]"
    """
    style = []
    if style_attr:
        if isinstance(style_attr, list):
            invalid = [
                attr
                for attr in style_attr
                if not isinstance(attr, CslStrStyleAttribute)
            ]
            if invalid:
                raise NotSupportedStyleAttribute(f"styles {invalid} are not supported")
            style.extend(style_attr)
        elif not isinstance(style_attr, CslStrStyleAttribute):
            raise NotSupportedStyleAttribute(f"{style_attr} is not supported")
        else:
            style.append(style_attr)

    if color is not None:
        if not isinstance(color, ColorIndex):
            raise NotSupportedStyleAttribute("Only valid ColorIndex are supported")

        style.append(str(color))

    style = " ".join(style)
    return f"[{style}]{text}[/{style}]"
