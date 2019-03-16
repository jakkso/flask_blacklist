"""Test Blacklist."""

from unittest import TestCase, main
from unittest.mock import MagicMock, Mock, patch

from flask_blacklist import Blacklist
from flask_blacklist.utilities import must_be_initialized, is_blacklisted, _get_blacklist


class TestBlacklist(TestCase):
    """Test Blacklist."""

    def test_deferred_initialization(self):
        """Deferred initialization works as expected.

        When Blacklist is constructed without being attached to a flask app,
        trying to use its methods will raise RuntimeErrors
        """
        blacklist = Blacklist()
        self.assertIsNone(blacklist.store)
        self.assertIsNone(blacklist.token_class)
        self.assertFalse(blacklist.initialized)
        with self.assertRaises(RuntimeError):
            # Trying to use methods when app is uninitialized raises RuntimeError
            blacklist.is_blacklisted("")
        with self.assertRaises(RuntimeError):
            blacklist.blacklist_jti("")

    def test_failed_initialization(self):
        """Specified methods are present on `token_class`.

        Trying to initialize Blacklist with a `token_class` that is lacking
        `get_blacklisted` or `blacklist_jti` will raise RuntimeErrors
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

        with self.assertRaises(RuntimeError):
            db_call = Mock().side_effect = Exception("Arbitrary database error message")
            token_class = MagicMock()
            token_class.get_blacklisted = db_call
            blacklist.init_app(app, token_class)

    def test_successful_init(self):
        """When required methods are present, store works as expected."""
        app = MagicMock()
        token_class = MagicMock()
        blacklist_jti = MagicMock(return_value=True)
        get_blacklisted = MagicMock(return_value=[{"jti": 123}, {"jti": 456}])
        app.extensions = {"sqlalchemy": True}
        token_class.blacklist_jti = blacklist_jti
        token_class.get_blacklisted = get_blacklisted
        # Patch out call to current_app.app_context.
        # Context is used by the database ORM, but that's being mocked out
        with patch('werkzeug.local.LocalProxy._get_current_object'):
            blacklist = Blacklist(app, token_class)
            get_blacklisted.assert_called()
            self.assertEqual(blacklist.store, {123, 456})
            self.assertTrue(blacklist.is_blacklisted(123))
            blacklist.blacklist_jti(789)
            self.assertTrue(789 in blacklist.store)
            blacklist_jti.assert_called()

    def test_magic_methods(self):
        """Magic methods return expected values"""
        bl = Blacklist()
        self.assertEqual(bl.__repr__(), 'Blacklist()')
        self.assertEqual(bl.__str__(), '<Blacklist with 0 item(s)>')
        self.assertTrue(Blacklist() == bl)
        self.assertFalse(bl == 1)
        bl.store = set()
        bl.store.add('123')
        self.assertEqual(bl.__str__(), '<Blacklist with 1 item(s)>')


class TestMustBeInitialized(TestCase):
    """Test Blacklist utilities."""

    def test_only_works_on_blacklist_obj(self):
        """`must_be_initialized` only raises if used on Blacklist method."""
        failure = MagicMock()
        failure.initialized = False
        failure.return_value = False
        val = test_func(failure)
        self.assertFalse(val)

    def test_must_be_initialized_success(self):
        """`must_be_initialized` does not raise error if blacklist initialized."""
        success = MagicMock()
        success.__class__.__name__ = 'Blacklist'
        success.initialized = True
        success.return_value = True

        val = test_func(success)
        # No error raised as initialized is set to True
        self.assertTrue(val)

    def test_must_be_initialized_failure(self):
        """`must_be_initialized` raises error if blacklist not initialized."""
        failure = MagicMock()
        failure.__class__.__name__ = 'Blacklist'
        failure.initialized = False
        failure.return_value = False
        # obj not initialized, so error is raised.
        with self.assertRaises(RuntimeError):
            test_func(failure)


class TestIsBlacklisted(TestCase):
    """Test `is_blacklisted` and `_get_blacklist`."""

    def test_get_blacklist(self):
        """`_get_blacklist` will return blacklist extension.

        Patch out werkzeug's LocalProxy class, as that's what actually returned by
        a call to flask.current_app.

        Figuring what exactly to patch a learning experience.
        """
        with patch('werkzeug.local.LocalProxy._get_current_object') as app:
            app_context = MagicMock()
            app_context.extensions.get.return_value = Blacklist()
            app.return_value = app_context
            blacklist_obj = _get_blacklist()
            app.assert_called()
            app_context.extensions.get.assert_called()
            self.assertEqual(Blacklist(), blacklist_obj)

    def test_is_blacklisted(self):
        """is_blacklisted will call correct methods.

        mocked out: `_get_blacklisted`
        """
        with patch('blacklist.utilities._get_blacklist') as ctx:
            bl = MagicMock()
            bl.is_blacklisted.return_value = True
            ctx.return_value = bl
            val = is_blacklisted('123')
            self.assertEqual(val, True)
            ctx.assert_called()
            bl.is_blacklisted.assert_called()


@must_be_initialized
def test_func(test_obj):
    """Return called test_obj"""
    return test_obj()


if __name__ == '__main__':
    main()  # pragma: no cover
