from pytest_bdd import scenario, given, when, then

@scenario('../features/login.feature', 'Successful login')
def test_login():
    pass

@given('the login page is loaded')
def login_page():
    pass

@when('I enter valid credentials')
def enter_credentials():
    pass

@then('I should be redirected to the dashboard')
def check_dashboard():
    pass
