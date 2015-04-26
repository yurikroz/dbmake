import dbmake.helper
from unittest import TestCase


class FooTestClass:
    def __init__(self):
        pass


class TestGetClass(TestCase):

    def test_import_fully_quallified_class(self):
        class_path = "dbmake.test.Foo"

        class_ = dbmake.helper.get_class(class_path)