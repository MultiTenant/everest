"""
This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Feb 4, 2011.
"""
from datetime import datetime
from everest.querying.filterparser import parse_filter
from everest.testing import Pep8CompliantTestCase
from pyparsing import ParseException

__docformat__ = 'reStructuredText en'
__all__ = ['QueryParserTestCase',
           ]


class QueryParserTestCase(Pep8CompliantTestCase):
    parser = None

    def set_up(self):
        self.parser = parse_filter

    def tear_down(self):
        pass

    def test_no_criterion_query(self):
        expr = ''
        self.assert_raises(ParseException, self.parser, expr)

    def test_one_criterion_query(self):
        expr = 'name:equal-to:"Nikos"'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 1)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'name')
        self.assert_equal(crit.operator, 'equal-to')
        self.assert_equal(list(crit.value), ['Nikos'])

    def test_one_criterion_query_with_many_values(self):
        expr = 'name:equal-to:"Nikos","Oliver","Andrew"'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 1)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'name')
        self.assert_equal(crit.operator, 'equal-to')
        self.assert_equal(list(crit.value), ['Nikos', 'Oliver', 'Andrew'])

    def test_multiple_criterion_query(self):
        expr = 'name:starts-with:"Ni"~name:ends-with:"kos"'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 2)
        crit1, crit2 = result.criteria
        self.assert_equal(crit1.name, 'name')
        self.assert_equal(crit1.operator, 'starts-with')
        self.assert_equal(list(crit1.value), ['Ni'])
        self.assert_equal(crit2.name, 'name')
        self.assert_equal(crit2.operator, 'ends-with')
        self.assert_equal(list(crit2.value), ['kos'])

    def test_one_criterion_query_with_integers(self):
        expr = 'age:equal-to:34,44'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 1)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'age')
        self.assert_equal(crit.operator, 'equal-to')
        self.assert_equal(list(crit.value), [34, 44])

    def test_one_criterion_query_with_integer_scientific_format(self):
        expr = 'volume:greater-than:5e+05'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 1)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'volume')
        self.assert_equal(crit.operator, 'greater-than')
        self.assert_equal(list(crit.value), [500000])

    def test_one_criterion_query_with_floats(self):
        expr = 'cost:greater-than:3.14'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 1)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'cost')
        self.assert_equal(crit.operator, 'greater-than')
        self.assert_equal(list(crit.value), [3.14])

    def test_one_criterion_query_with_floats_scientific_format(self):
        expr = 'volume:greater-than:5.5e-05'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 1)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'volume')
        self.assert_equal(crit.operator, 'greater-than')
        self.assert_equal(list(crit.value), [5.5e-05])

    def test_one_criterion_query_with_floats_scientific_format_negative(self):
        expr = 'volume:greater-than:5e-05'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 1)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'volume')
        self.assert_equal(crit.operator, 'greater-than')
        self.assert_equal(list(crit.value), [5e-05])

    def test_one_criterion_query_with_url(self):
        url = 'http://everest.org/species/human'
        expr = 'species:equal-to:%s' % url
        result = self.parser(expr)
        value = result.criteria[0].value[0]
        self.assert_equal(value, url)

    def test_multiple_criterion_query_with_url(self):
        url1 = 'http://everest.org/species/human'
        url2 = 'http://everest.org/species/rat'
        expr = 'species:equal-to:%s,%s' % (url1, url2)
        result = self.parser(expr)
        value1 = result.criteria[0].value[0]
        value2 = result.criteria[0].value[1]
        self.assert_equal(value1, url1)
        self.assert_equal(value2, url2)

    def test_multiple_criterion_query_with_different_value_types(self):
        expr = 'name:starts-with:"Ni","Ol","An"~' \
               'age:equal-to:34,44,54~' \
               'phone-number:starts-with:1,2,3~' \
               'discount:equal-to:-20,-30~'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 4)
        crit1, crit2, crit3, crit4 = result.criteria
        self.assert_equal(crit1.name, 'name')
        self.assert_equal(crit1.operator, 'starts-with')
        self.assert_equal(list(crit1.value), ['Ni', 'Ol', 'An'])
        self.assert_equal(crit2.name, 'age')
        self.assert_equal(crit2.operator, 'equal-to')
        self.assert_equal(list(crit2.value), [34, 44, 54])
        self.assert_equal(crit3.name, 'phone-number')
        self.assert_equal(crit3.operator, 'starts-with')
        self.assert_equal(list(crit3.value), [1, 2, 3])
        self.assert_equal(crit4.name, 'discount')
        self.assert_equal(crit4.operator, 'equal-to')
        self.assert_equal(list(crit4.value), [-20, -30])

    def test_one_text_criterion_query_with_spaces(self):
        expr = 'name:equal-to:"Nikos Papagrigoriou"'
        result = self.parser(expr)
        crit = result.criteria[0]
        self.assert_equal(list(crit.value), ['Nikos Papagrigoriou'])

    def test_one_criterion_with_only_comma(self):
        expr = 'name:equal-to:,'
        result = self.parser(expr)
        crit = result.criteria[0]
        self.assert_equal(list(crit.value), [])

    def test_multiple_criterion_query_with_misplaced_commas(self):
        expr = 'name:starts-with:"Ni", "Ol", ,"An"~' \
               'age:equal-to:34, 44, 54,~' \
               'phone-number:starts-with:,1,2,3~' \
               'discount:equal-to:,-20,,-30,'
        result = self.parser(expr)
        self.assert_equal(len(result.criteria), 4)
        crit1, crit2, crit3, crit4 = result.criteria
        self.assert_equal(crit1.name, 'name')
        self.assert_equal(crit1.operator, 'starts-with')
        self.assert_equal(list(crit1.value), ['Ni', 'Ol', 'An'])
        self.assert_equal(crit2.name, 'age')
        self.assert_equal(crit2.operator, 'equal-to')
        self.assert_equal(list(crit2.value), [34, 44, 54])
        self.assert_equal(crit3.name, 'phone-number')
        self.assert_equal(crit3.operator, 'starts-with')
        self.assert_equal(list(crit3.value), [1, 2, 3])
        self.assert_equal(crit4.name, 'discount')
        self.assert_equal(crit4.operator, 'equal-to')
        self.assert_equal(list(crit4.value), [-20, -30])

    def test_float_and_int(self):
        expr = 'age:less-than:12~height:less-than:5.2'
        result = self.parser(expr)
        crit1 = result.criteria[0]
        crit2 = result.criteria[1]
        self.assert_true(isinstance(crit1.value[0], int))
        self.assert_true(isinstance(crit2.value[0], float))

    def test_valid_dotted_names(self):
        expr = 'user.age:less-than:12'
        result = self.parser(expr)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'user.age')
        expr = 'user.address.street:equal-to:Main'
        result = self.parser(expr)
        crit = result.criteria[0]
        self.assert_equal(crit.name, 'user.address.street')

    def test_invalid_dotted_names(self):
        expr = 'user.age.:less-than:12'
        self.assert_raises(ParseException, self.parser, expr)
        expr = '.user.age:less-than:12'
        self.assert_raises(ParseException, self.parser, expr)
        expr = 'user..age:less-than:12'
        self.assert_raises(ParseException, self.parser, expr)

    def test_valid_date(self):
        expr = 'birthday:equal-to:"1966-04-21T15:23:01Z"'
        result = self.parser(expr)
        crit = result.criteria[0]
        self.assert_true(isinstance(crit.value[0], datetime))
        dt = crit.value[0]
        self.assert_equal(dt.year, 1966)
        self.assert_equal(dt.month, 4)
        self.assert_equal(dt.day, 21)
        self.assert_equal(dt.hour, 15)
        self.assert_equal(dt.minute, 23)
        self.assert_equal(dt.second, 1)

    def test_invalid_dates(self):
        # Violations of the regex.
        expr = 'birthday:equal-to:"19661-04-21T15:23:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        expr = 'birthday:equal-to:"19661-041-21T15:23:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        expr = 'birthday:equal-to:"1966-04-211T15:23:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        expr = 'birthday:equal-to:"1966-04-21T151:23:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        expr = 'birthday:equal-to:"1966-04-21T15:231:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        # Violations of the allowed values.
        expr = 'birthday:equal-to:"1966-13-21T15:23:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        expr = 'birthday:equal-to:"1966-04-32T15:23:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        expr = 'birthday:equal-to:"1966-04-21T24:23:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))
        expr = 'birthday:equal-to:"1966-04-21T15:61:00Z"'
        result = self.parser(expr)
        self.assert_false(isinstance(result.criteria[0].value[0], datetime))