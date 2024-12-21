Feature: How to use scenario outlines

  Scenario Outline: Just a scenario
    Given param1 is <param1> and param2 is <param2>
    When having table
      | cell1 | cell2  |
      | 123   | 234    |
      | 44    | 555    |
      | 7777  | 434343 |
    Then all params <param1> <param2> <param3>

    Examples:
      | param1 | param2 | param3 |
      | aaa    | bbb    | ccc    |
      | ddd    | eee    | fff    |

    Examples:
      | param1 | param2 | param3 |
      | 11     | 22     | 33     |
      | 44     | 55     | 66     |

