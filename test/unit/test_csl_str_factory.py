import pytest

from utils.csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex
from exceptions import NotSupportedStyleAttribute


@pytest.fixture(scope="session")
def text():
    yield "Hello, World!"


def test_create_str_single_attribute_ok(text):
    style_attr = CslStrStyleAttribute.BOLD
    expected = f"[{style_attr}]{text}[/{style_attr}]"
    assert csl_str_factory(text=text, style_attr=style_attr) == expected


def test_create_str_list_of_attributes_ok(text):
    styles = [CslStrStyleAttribute.BOLD, CslStrStyleAttribute.UNDERLINE]
    style_attr = " ".join(styles)
    expected = f"[{style_attr}]{text}[/{style_attr}]"
    assert csl_str_factory(text=text, style_attr=styles) == expected


def test_not_supported_attribute_error(text):
    style_attr = "CAT"
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text=text, style_attr=style_attr)

    assert str(e.value) == f"{style_attr} is not supported"


def test_not_supported_attribute_in_list_error(text):
    styles = [CslStrStyleAttribute.BOLD, CslStrStyleAttribute.UNDERLINE, "CAT"]
    style_attr = " ".join(styles)
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text=text, style_attr=styles)

    assert str(e.value) == f"styles {["CAT"]} are not supported"


def test_not_supported_attributes_in_list_error(text):
    styles = ["DOG", "CAT"]
    style_attr = " ".join(styles)
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text=text, style_attr=styles)

    assert str(e.value) == f"styles {styles} are not supported"


def test_valid_color_index_ok(text):
    color = ColorIndex(1)
    assert csl_str_factory(text, color=color) == f"[{color}]{text}[/{color}]"


def test_color_index_error_not_valid_type(text):
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text, color=1)

    assert str(e.value) == "Only valid ColorIndex are supported"


def test_csl_factory_with_color_and_single_styling(text):
    color = ColorIndex(1)
    style_attr = CslStrStyleAttribute.BOLD
    assert (
        csl_str_factory(text, style_attr, color)
        == f"[{style_attr} {color}]{text}[/{style_attr} {color}]"
    )


def test_csl_factory_with_color_and_multiple_styling(text):
    color = ColorIndex(1)
    style_attr = [CslStrStyleAttribute.BOLD, CslStrStyleAttribute.BLINK]
    style_str = " ".join(style_attr) + f" {color}"
    assert (
        csl_str_factory(text, style_attr, color) == f"[{style_str}]{text}[/{style_str}]"
    )


def test_csl_factory_valid_style_attr_invalid_color_error(text):
    color = 1
    style_attr = [CslStrStyleAttribute.BOLD, CslStrStyleAttribute.BLINK]
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text, style_attr, color)

    assert str(e.value) == "Only valid ColorIndex are supported"


def test_csl_factory_valid_color_invalid_style_attr_error(text):
    color = ColorIndex(1)
    style_attr = [CslStrStyleAttribute.BOLD, "CAT"]
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text, style_attr, color)

    assert str(e.value) == f"styles ['CAT'] are not supported"


def test_csl_factory_valid_color_invalid_single_style_attr_error(text):
    style_attr = "CAT"
    color = ColorIndex(2)
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text, style_attr, color)

    assert str(e.value) == f"{style_attr} is not supported"
