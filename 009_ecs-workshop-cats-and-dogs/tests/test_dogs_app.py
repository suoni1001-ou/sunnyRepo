import importlib.util
import pathlib
import sys
import types
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_PATH = ROOT / 'ecsworkshop' / 'dogs' / 'app.py'

spec = importlib.util.spec_from_file_location('dogs_app', APP_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules['dogs_app'] = module
spec.loader.exec_module(module)


class DogsAppTests(unittest.TestCase):
    def setUp(self):
        self.client = module.app.test_client()

    def test_get_conn_initializes_configured_schema(self):
        fake_conn = mock.MagicMock()
        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

        with mock.patch.object(module, 'DB_NAME', 'database-1'), \
            mock.patch.object(module.pymysql, 'connect', return_value=fake_conn) as connect:
            module.get_conn()

        self.assertNotIn('database', connect.call_args.kwargs)
        fake_cursor.execute.assert_called_once_with(
            'CREATE DATABASE IF NOT EXISTS `database-1`'
        )
        fake_conn.select_db.assert_called_once_with('database-1')

    def test_dogs_route_accepts_trailing_slash(self):
        fake_conn = mock.MagicMock()
        fake_cursor = fake_conn.__enter__.return_value.__enter__.return_value
        fake_cursor.fetchone.return_value = {'cnt': 7}

        with mock.patch.object(module, 'get_conn', return_value=fake_conn):
            resp = self.client.get('/dogs/')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Aurora 接続成功', resp.get_data(as_text=True))
        self.assertIn('7', resp.get_data(as_text=True))

    def test_db_error_shows_user_friendly_message(self):
        with mock.patch.object(module, 'get_conn', side_effect=Exception('db down')):
            resp = self.client.get('/dogs')

        body = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Aurora 接続エラー', body)
        self.assertIn('取得できません', body)


if __name__ == '__main__':
    unittest.main()
