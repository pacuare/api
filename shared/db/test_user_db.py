from .user_db import get_user_database


def test_get_user_database():
    assert get_user_database('edu@pacuare.dev') == 'user_edu__pacuare_dev'
