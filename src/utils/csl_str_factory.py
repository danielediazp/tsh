from enum import auto, StrEnum

from exceptions import NotSupportedStyleAttribute


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


def csl_str_factory(
    text: str, style_attr: CslStrStyleAttribute | list[CslStrStyleAttribute]
) -> str:
    """
    Creates a formatted `rich.console` string

    Args:
        text (str): the text to apply the format to
        style (CslStrStyleAttribute): the format that will be apply to the text

    Returns:
        str: in the format `[style_attr] text [/style_attr]`

    Raises:
        NotSupportedStyleAttribute: if `style_attr` is not supported by the `CslStrStyleAttribute` enum

    Example:
        >>> csl_str_factory("Hello", CslStrStyleAttribute.BOLD)
        >>> "[bold]Hello[/bold]"
    """
    if isinstance(style_attr, list):
        invalid = [
            attr for attr in style_attr if not isinstance(attr, CslStrStyleAttribute)
        ]
        if invalid:
            raise NotSupportedStyleAttribute(f"styles {invalid} are not supported")
        style_attr = " ".join(style_attr)
    elif not isinstance(style_attr, CslStrStyleAttribute):
        raise NotSupportedStyleAttribute(f"{style_attr} is not supported")

    return f"[{style_attr}]{text}[/{style_attr}]"
