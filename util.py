from collections.abc import Callable


class Maybe[T]:
    """
    Wraps a value that may be `T` or `None`, providing methods for conditionally using that value or short-circuiting
    to `None` without longer checks.
    """
    def __init__(self, val: T | None) -> None:
        """
        :param val: A value to wrap.
        """
        self.val = val

    def __repr__(self) -> str:
        return f'Maybe({self.val!r})'

    def then[R](self, func: Callable[[T], R]) -> R | None:
        """
        Call `func` with the wrapped value as the argument and return its value, or return `None` if the wrapped value
        is `None`.

        :param func: A `Callable` which takes a type of the possible wrapped value (`T`) and can return any type (`R`).
        """
        return func(self.val) if self.val is not None else None

    def unwrap(self) -> T:
        """Return the wrapped value if it is not `None`, otherwise raise `ValueError`."""
        if self.val is None:
            raise ValueError('Maybe value unwrapped into None')
        return self.val
