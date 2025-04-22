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

def test_not_supported_attribute_in_list_error():
    styles = [CslStrStyleAttribute.BOLD, CslStrStyleAttribute.UNDERLINE, "CAT"]
    style_attr = " ".join(styles)
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text=text, style_attr=styles)
    
    assert str(e.value) == f"styles {["CAT"]} are not supported"

def test_not_supported_attributes_in_list_error():
    styles = ["DOG", "CAT"]
    style_attr = " ".join(styles)
    with pytest.raises(NotSupportedStyleAttribute) as e:
        csl_str_factory(text=text, style_attr=styles)
    
    assert str(e.value) == f"styles {styles} are not supported"

def test_valid_color_index_ok():
    color = ColorIndex(1)
    text = "Hello, World!"
    assert csl_str_factory(text, color=color) == f"[{color}]{text}[/{color}]"
