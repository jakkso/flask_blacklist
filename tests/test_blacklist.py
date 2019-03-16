"""Test Blacklist class."""

from unittest import main, TestCase
from unittest.mock import MagicMock

from blacklist import Blacklist


class TestBlacklist(TestCase):
    """Test Blacklist class."""

    def test_deferred_initialization(self):
        """Check that deferred initializations works as expected."""
        blacklist = Blacklist()
        self.assertIsNone(blacklist.store)
        self.assertIsNone(blacklist.token_class)
        self.assertFalse(blacklist.initialized)
        with self.assertRaises(RuntimeError):
            # Trying to use methods when app is uninitialized raises RuntimeError
            blacklist.is_blacklisted("")
            blacklist.blacklist_jti("")

    def test_failed_init(self):
        """`token_class` object must contain specific attributes.

        Checks that attempting to initialize object with a token_class object missing
        the required attrs will raise RuntimeError
        """
        app = MagicMock()
        app.extensions = None
        blacklist_jti = MagicMock(return_value=True)
        get_blacklisted = MagicMock(return_value=[{"jti": 123}, {"jti": 456}])

        blacklist = Blacklist()
        # Test for each missing attr
        with self.assertRaises(RuntimeError):
            missing_get_blacklisted = MagicMock()
            missing_get_blacklisted.get_blacklisted = None
            missing_get_blacklisted.blacklist_jti = blacklist_jti
            blacklist.init_app(app, missing_get_blacklisted)
        with self.assertRaises(RuntimeError):
            missing_blacklist_jti = MagicMock()
            missing_blacklist_jti.blacklist_jti = None
            missing_blacklist_jti.get_blacklisted = get_blacklisted
            blacklist.init_app(app, missing_blacklist_jti)

    def test_successful_init(self):
        """Check that successful initialization works as expected."""
        app = MagicMock()
        token_class = MagicMock()
        blacklist_jti = MagicMock(return_value=True)
        get_blacklisted = MagicMock(return_value=[{"jti": 123}, {"jti": 456}])
        app.extensions = {"sqlalchemy": True}
        token_class.blacklist_jti = blacklist_jti
        token_class.get_blacklisted = get_blacklisted

        blacklist = Blacklist(app, token_class)
        get_blacklisted.assert_called()
        self.assertEqual(blacklist.store, {123, 456})
        self.assertTrue(blacklist.is_blacklisted(123))
        blacklist.blacklist_jti(789)
        self.assertTrue(789 in blacklist.store)
        blacklist_jti.assert_called()


if __name__ == '__main__':
    main()
