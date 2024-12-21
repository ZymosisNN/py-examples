Feature: Experimental feature
  Description of experimental feature

  Scenario Outline: Experimental scenario
    Given Working entity with shit
      | opt1   | opt2   |
      | value1 | value2 |
      | value3 | value4 |
    When Performs operation with <param1>, part of next param <param2>
    Then Result is "<param3>"
    Examples:
      | param1 | param2 | param3 |
      | aaa    | bbb    | ccc    |
      | ddd    | eee    | fff    |


