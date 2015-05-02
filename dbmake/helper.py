import pyclbr
import re


def find_string_between(s, start, end):
    """
    Returns a substring between two other substrings
    :param s: Text
    :param start: A substring to start extracting the desired substring from
    :param end: A substring to stop extracting the desired substring on
    :return:
    """
    return re.search('%s(.*)%s' % (start, end), s).group(1)


def underscore_to_camelcase(s):
    l = s.split("_")
    return "".join(map(str.capitalize, l[:]))


def camelcase(s, delimeter="_"):
    l = s.split(delimeter)
    return "".join(map(str.capitalize, l[:]))


def get_module_classes(module_name):
    return pyclbr.readmodule(module_name).keys()


def get_class(fully_qualified_path):
    # Source: http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
    parts = fully_qualified_path.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_class_instance(fully_qualified_path, module_name, class_name, *instantiation):
    """
    Returns an instantiated class for the given string descriptors
    :param fully_qualified_path: The path to the module eg("Utilities.Printer")
    :param module_name: The module name eg("Printer")
    :param class_name: The class name eg("ScreenPrinter")
    :param instantiation: Any fields required to instantiate the class
    :return: An instance of the class
    """
    p = __import__(fully_qualified_path)
    m = getattr(p, module_name)
    c = getattr(m, class_name)
    instance = c(*instantiation)
    return instance