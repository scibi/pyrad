import unittest
import operator
import os
from StringIO import StringIO
from pyrad.tests import home
from pyrad.dictionary import Attribute
from pyrad.dictionary import Dictionary
from pyrad.dictionary import ParseError
from pyrad.tools import DecodeAttr


class DictionaryInterfaceTests(unittest.TestCase):
    def testEmptyDictionary(self):
        dict=Dictionary()
        self.assertEqual(len(dict), 0)

    def testContainment(self):
        dict=Dictionary()
        self.assertEqual("test" in dict, False)
        self.assertEqual(dict.has_key("test"), False)
        dict.attributes["test"]="dummy"
        self.assertEqual("test" in dict, True)
        self.assertEqual(dict.has_key("test"), True)

    def testReadonlyContainer(self):
        dict=Dictionary()
        self.assertRaises(AttributeError,
                operator.setitem, dict, "test", "dummy")
        self.assertRaises(AttributeError,
                operator.attrgetter("clear"), dict)
        self.assertRaises(AttributeError,
                operator.attrgetter("update"), dict)



class DictionaryParsingTests(unittest.TestCase):
    def setUp(self):
        self.path=os.path.join(home, "tests", "data")

    def testParseEmptyDictionary(self):
        dict=Dictionary(StringIO(""))
        self.assertEqual(len(dict), 0)

    def testParseSimpleDictionary(self):
        dict=Dictionary(os.path.join(self.path, "simple"))
        self.assertEqual(len(dict), 8)
        values = [
                ( "Test-String", 1, "string" ),
                ( "Test-Octets", 2, "octets" ),
                ( "Test-Integer", 3, "integer" ),
                ( "Test-Ip-Address", 4, "ipaddr" ),
                ( "Test-Ipv6-Address", 5, "ipv6addr" ),
                ( "Test-If-Id", 6, "ifid" ),
                ( "Test-Date", 7, "date" ),
                ( "Test-Abinary", 8, "abinary" ),
                ]

        for (attr, code, type) in values:
            attr=dict[attr]
            self.assertEqual(attr.code, code)
            self.assertEqual(attr.type, type)

    def testAttributeTooFewColumnsError(self):
        dict=Dictionary()
        self.assertRaises(ParseError, dict.ReadDictionary,
                StringIO("ATTRIBUTE Oops-Too-Few-Columns"))
        try:
            dict.ReadDictionary(StringIO("ATTRIBUTE Oops-Too-Few-Columns"))
        except ParseError, e:
            self.assertEqual(e.linenumber, 1)
            self.assertEqual("attribute" in str(e), True)


    def testAttributeUnknownTypeError(self):
        dict=Dictionary()
        self.assertRaises(ParseError, dict.ReadDictionary,
                StringIO("ATTRIBUTE Test-Type 1 dummy"))
        try:
            dict.ReadDictionary(StringIO("ATTRIBUTE Test-Type 1 dummy"))
        except ParseError, e:
            self.assertEqual(e.linenumber, 1)
            self.assertEqual("dummy" in str(e), True)


    def testValueTooFewColumnsError(self):
        dict=Dictionary()
        self.assertRaises(ParseError, dict.ReadDictionary,
                StringIO("VALUE Oops-Too-Few-Columns"))
        try:
            dict.ReadDictionary(StringIO("VALUE Oops-Too-Few-Columns"))
        except ParseError, e:
            self.assertEqual(e.linenumber, 1)
            self.assertEqual("value" in str(e), True)


    def testValueForUnknownAttributeError(self):
        dict=Dictionary()
        self.assertRaises(ParseError, dict.ReadDictionary,
                StringIO("VALUE Test-Attribute Test-Text 1"))
        try:
            dict.ReadDictionary(StringIO("VALUE Test-Attribute Test-Text 1"))
        except ParseError, e:
            self.assertEqual(e.linenumber, 1)
            self.assertEqual("unknown attribute" in str(e), True)


    def testIntegerValueParsing(self):
        dict=Dictionary(os.path.join(self.path, "simple"))
        self.assertEqual(len(dict["Test-Integer"].values), 0)
        dict.ReadDictionary(StringIO("VALUE Test-Integer Value-Six 5"))
        self.assertEqual(len(dict["Test-Integer"].values), 1)
        self.assertEqual(
                DecodeAttr("integer", dict["Test-Integer"].values["Value-Six"]),
                5)


    def testStringValueParsing(self):
        dict=Dictionary(os.path.join(self.path, "simple"))
        self.assertEqual(len(dict["Test-String"].values), 0)
        dict.ReadDictionary(StringIO("VALUE Test-String Value-Custard custardpie"))
        self.assertEqual(len(dict["Test-String"].values), 1)
        self.assertEqual(
                DecodeAttr("string", dict["Test-String"].values["Value-Custard"]),
                "custardpie")
