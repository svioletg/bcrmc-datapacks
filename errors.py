class WrongFileSuffixWarning(Warning):
    """Emitted when a file's final suffix/extension is different from what was expected.

    Use :class:`WrongFileSuffixError` if a full exception is needed.
    """

class KeyExistsError(Exception):
    """Raised when a key already exists in a mapping object where overwriting it is not allowed."""
class WrongFileSuffixError(Exception):
    """Raised when a file's final suffix/extension is different from what was expected.

    Use :class:`WrongFileSuffixWarning` if only a warning is needed.
    """
