import pytest
import functools
from main import check_date_publication


def case_for_tests(cases):
    def decorator(f):
        def wrapper(*args, **kwargs):
            for case_ in cases:
                args_ = args + (case_,)
                res = f(*args_, **kwargs)    
        return wrapper        
    return decorator


@case_for_tests([
    '2021-08-10T13:13:13Z',
    '2021-07-30T13:13:13Z',
])
def test_check_dste_publication_true(cases_):
    print(f'\n{cases_=} - {check_date_publication(cases_)=}')
    assert check_date_publication(cases_) == True


@case_for_tests([
    '2021-01-10T13:13:13Z',
    '2021-07-20T13:13:13Z',
])
def test_check_dste_publication_false(cases_):
    print(f'\n{cases_=} - {check_date_publication(cases_)=}')
    assert check_date_publication(cases_) == False


if __name__ == "__main__":
    ...