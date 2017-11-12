from bs4 import BeautifulSoup

from .decorators import login_required
from .utils.constants import BASE_URL, SERVER_DOWN_MSG
from .utils.helpers import get_session, print_table


def get_description(problem_code):
    """
    :desc: Retrieves a particular problem description.
    :param: `problem_code` Code of the problem.
    :return: `str` [description / Not Found / Server down]
    """

    session = get_session()
    req_obj = session.get(BASE_URL + '/problems/' + problem_code)

    if req_obj.status_code == 200:
        problem_html = req_obj.text
        soup = BeautifulSoup(problem_html, 'html.parser')
        if soup.find(id='problem-code'):
            content = soup.find_all('div', class_='content')[1]
            content.find_all('h3')[0].extract()
            content.find_all('h3')[0].extract()
            problem_info = soup.find_all('table')[2].text
            return content.text + problem_info
        else:
            return 'Problem not found'
    else:
        return SERVER_DOWN_MSG


def get_form_token(problem_submit_html):
    """
    :desc: Retrieves problem submission form token.
    :param: `problem_submit_html` HTML text containing problem submission form.
    :return: `str` form token value
    """

    soup = BeautifulSoup(problem_submit_html, 'html.parser')
    form = soup.find('form', id='problem-submission')
    return form.find('input', id='edit-problem-submission-form-token')['value']


def get_error_table(status_code):
    """
    :desc: Retrieves error status table.
    :param: `status_code` Status code of the submitted problem.
    :return: `str` error status table
    """

    session = get_session()
    req_obj = session.get(BASE_URL + '/error_status_table/' + status_code)
    if req_obj.status_code == 200:
        return req_obj.text

    return None


def get_compilation_error(status_code):
    """
    :desc: Retrieves compilation error text.
    :param: `status_code` Status code of the submitted problem.
    :return: `str` Compilation error text.
    """

    session = get_session()
    req_obj = session.get(BASE_URL + '/view/error/' + status_code)

    if req_obj.status_code == 200:
        soup = BeautifulSoup(req_obj.text, 'html.parser')
        return soup.find('div', class_='cc-error-txt').text

    return SERVER_DOWN_MSG


def get_language_code(problem_submit_html, language):
    """
    :desc: Retrieves language code.
    :param: `problem_submit_html` HTML text containing problem submission form.
            `language` Language Name (eg. Python3, C++, etc.)
    :return: `str` Language code.
    """

    soup = BeautifulSoup(problem_submit_html, 'html.parser')
    form = soup.find('form', id='problem-submission')
    languages_dropdown = form.find('select', id='edit-language')
    language_options = languages_dropdown.find_all('option')

    for option in language_options:
        if language.lower() + '(' in option.text.lower():
            return option['value']


@login_required
def submit_problem(problem_code, solution_file, language):
    """
    :desc: Submits the problem.
    :param: `problem_code` Code of the problem.
            `solution_file` Path of the solution file.
            `language` Language Name (eg. Python3, C++, etc.)
    :return: None
    """

    session = get_session()
    req_obj = session.get(BASE_URL + '/submit/' + problem_code)

    if req_obj.status_code == 200:
        form_token = get_form_token(req_obj.text)
        language_code = get_language_code(req_obj.text, language)
    else:
        print (SERVER_DOWN_MSG)
        return

    try:
        solution_file_obj = open(solution_file)
    except IOError:
        print ('Solution file not found. Please provide a valid path.')

    post_data = {
        'language': language_code,
        'problem_code': problem_code,
        'form_id': 'problem_submission',
        'form_token': form_token,
    }
    post_files = { 'files[sourcefile]': solution_file_obj }

    req_obj = session.post(BASE_URL + '/submit/' + problem_code, data=post_data, files=post_files)
    if req_obj.status_code == 200:
        print ('Problem Submitted...')
        print ('Running code...\n')

        status_code = req_obj.url.split('/')[-1]

        while True:
            status_req = session.get(BASE_URL + '/get_submission_status/' + status_code)
            try:
                status_json = status_req.json()
            except ValueError:
                continue
            result_code = status_json['result_code']

            if result_code != 'wait':
                if result_code == 'compile':
                    print (u'Compilation error.\n{0}'.format(get_compilation_error(status_code)))
                elif result_code == 'runtime':
                    print (u'Runtime error. {0}\n'.format(status_json['signal']))
                elif result_code == 'wrong':
                    print ('Wrong answer\n')
                elif result_code == 'accepted':
                    print ('Correct answer\n')

                print_table(get_error_table(status_code))
                break
    else:
        print (SERVER_DOWN_MSG)


def search_problems(contest_code):
    """
    :desc: Retrieves contest problems.
    :param: `contest_code` Code of the contest. (Eg, OCT17, COOK88)
    :return: None
    """

    session = get_session()
    req_obj = session.get(BASE_URL + '/' + contest_code)

    if req_obj.status_code == 200:
        soup = BeautifulSoup(req_obj.text, 'html.parser')
        table_html = str(soup.find_all('table')[1])

        print_table(table_html)
    else:
        print (SERVER_DOWN_MSG)

