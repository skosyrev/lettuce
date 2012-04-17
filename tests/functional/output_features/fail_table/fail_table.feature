Feature: Table Success
  Scenario: Add two numbers

    Given I have 0 bucks
    And that I have these items:
      | name    | price  |
      | Porsche | 200000 |
      | Ferrari | 400000 |
      | Bugatti | 1000000|

    When I sell the "Ferrari"
    And I sell the "Porsche"
    Then I have 600000 bucks
    And my garage contains:
      | name    | price  |
      | Bugatti | 1000000|
      | Porsche | 200000 |
