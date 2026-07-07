Feature: User Login
  Scenario: Successful login
    Given the login page is loaded
    When I enter valid credentials
    Then I should be redirected to the dashboard
