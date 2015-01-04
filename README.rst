``masapan``
-----------
A static coverage framework that allows the definition of rules for coverage
and then detects the actual test coverage against those rules.

Unlike traditional coverage tools for ensuring test coverage of the code under
test, this framework provides a way to determine coverage against a different
API.

Primarily created to deal with an independent test suite against the Amazon S3
API, and ensure that every documented bit of the API has a matching test case.


how does it work?
-----------------
Define the cases in dictionaries that have all the combinatorial data and
register it by using the ``mazapan.register`` call. Once those rules are in
place, ``mazapan`` can then run and collect all tests in a certain path and
match the test names against the cases previously registered.

For the match to happen, the reporting engine does some normalization, so if
there is a case defined like::

    {
        'operations': {
            'bucket': {
                'requests': ['get', 'post'],
                'errors': ['AccessDenied'],
            },
        },
    }

That would mean that there should be tests in the path:
``operations/bucket.py`` and two classes with three tests::


    class TestRequests(object):

        def test_get(self):
            pass

        def test_post(self):
            pass


    class TestErrors(object):

        def test_accessdenied(self):
            pass

For any test method, the ``masapan`` engine will strip the leading ``test_``
from the method name, and will normalize the rest of it to a lower case string
and converting underscores to spaces.


defining cases
--------------
Cases can be defined loosely, as long as they are dictionaries that represent
a path to a test module that has classes and test methods it should be OK.

For clarity, it might be better to define them separately so that it is easier
to read/understand the rules for the cases::

    from mazapan import register

    # Bucket
    register(path='operations/bucket',
        {
            'requests': ['get', 'post'],
             'errors': ['AccessDenied'],
        }
    )

    # Objects
    register(path='operations/objects',
        {
            'requests': ['get', 'post', 'put', 'delete'],
             'errors': ['AccessDenied', 'InvalidSignature'],
        }
    )


