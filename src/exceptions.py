class NotSupportedStyleAttribute(Exception):
    """
    Custom exception for not supported Style Attributes in `rich.console` object
    """

    pass


class ModelNotFoundError(Exception):
    """
    Custom exception for not found Models in the database.
    """

    pass


class InvalidColorIndex(Exception):
    """
    Custom exception for invalid color Index. ColorIndex val must be
    between 1 and 255.
    """

    pass


class InvalidStateTransition(Exception):
    """
    Custom Exception for Invalid state transition. Raised any time the transition
    between `App` state is invalid.
    """

    pass
