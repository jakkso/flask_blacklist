"""Test Blacklist class."""

from flask import current_app


def must_be_initialized(method):
    """Decorate Blacklist class methods.

    Ensures that Blacklist has been initialized.
    :param method Blacklist class method
    :raises RuntimeError:
    """
    def wrapper(*args, **kwargs):
        if args[0].__class__.__name__ == "Blacklist":
            if args[0].initialized is False:
                raise RuntimeError("Blacklist has not been initialized.")
        return method(*args, **kwargs)

    return wrapper


def _get_blacklist():
    """Return Blacklist extension attached to Flask app."""
    with current_app.app_context() as app:
        blacklist = app.extensions.get('blacklist')
        return blacklist


def is_blacklisted(jti: str) -> bool:
    """Return blacklist status of `jti`.

    :param jti: str
    :return: bool
    """
    bl = _get_blacklist()
    return bl.is_blacklisted(jti)
