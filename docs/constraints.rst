.. _constraints:

Allowed constraints for all of types:
  * **default** (*string*) - default value
  * **required** (*true*/*false*) - required field

Allowed constraints for *integer*/*float* fields:
  * **max_value** (*integer*/*float*) - maximum value
  * **min_value** (*integer*/*float*) - minimum value

Allowed constraints for *string* fields:
  * **lowercase** (*true*/*false*) - field can only contain
    lowercase values
  * **uppercase** (*true*/*false*) - field can only contain
    uppercase values
  * **alphanumeric** (*true*/*false*) - field can only contain
    alpha-numeric values
  * **regexp** (*regex expression*) - field can only contain value matched
    to the regex expression
  * **alpha** (*true*/*false*) - field can only contain letters
  * **numeric** (*true*/*false*) - field can only contain numbers
  * **min_length** (*integer*) - minimum length of string
  * **max_length** (*integer*) - maximum length of string
