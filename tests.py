import pytest
import functools

from main import check_date_publication, parsing_page

html_text = '''
<!DOCTYPE html>
<html>
 <head>
  <meta charset="utf-8" />
  <title>HTML5</title>
  <!--[if IE]>
   <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
  <![endif]-->
  <style>
   article, aside, details, figcaption, figure, footer,header,
   hgroup, menu, nav, section { display: block; }
  </style>
 </head>
 <body>
  <p>Привет, мир</p>
  <a href="./html5shiv.googlecode.com/svn/trunk/html5.com" datatime='2021-08-10T13:13:13Z'>
   123
  </a>
  <a href="./html5shiv.googlecode.com/svn/trunk/html5.com" datatime='2021-08-10T13:13:13Z'>
  '2021-08-10T13:13:13Z' 
  </a> 
 </body>
</html>
'''

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


def test_parsed_page():
    assert parsing_page(str(html_text), par_search='a') == set('http://html5shiv.googlecode.com/svn/trunk/html5.com',)


if __name__ == "__main__":
    print(parsing_page(html_text, par_search='a'))