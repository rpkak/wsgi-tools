# Filtered Parser

API-Reference: {py:meth}`wsgi_tools.filtered_parser`

This includes the WSGI-app {py:meth}`wsgi_tools.filtered_parser.FilteredJSONParser`. It is structured like the {py:meth}`wsgi_tools.parser.JSONParser` described {ref}`here<parser>`, but does not accept every json-string.

What json-strings to accept is configured in filters.

A filter is a callable, which has the value to control as an arg and returns a tuple of the boolean, which tells you if this value is allowed and the reason as a string. If the value is allowed, the reason is not relevant and can be an empty string or `None`.

There are the premade filters {py:meth}`wsgi_tools.filtered_parser.Int`, {py:meth}`wsgi_tools.filtered_parser.Float`, {py:meth}`wsgi_tools.filtered_parser.Boolean`, {py:meth}`wsgi_tools.filtered_parser.Object`, {py:meth}`wsgi_tools.filtered_parser.String`, {py:meth}`wsgi_tools.filtered_parser.Options` and {py:meth}`wsgi_tools.filtered_parser.List`.

- {py:meth}`wsgi_tools.filtered_parser.Boolean` and {py:meth}`wsgi_tools.filtered_parser.String` are unlike the other premade filters directly filters. They don't have to be construced.

- {py:meth}`wsgi_tools.filtered_parser.Int` and {py:meth}`wsgi_tools.filtered_parser.Float` have the two optional args `min` and `max`.

- {py:meth}`wsgi_tools.filtered_parser.Options` has to be construced with other filters. If one of them allows the value, the {py:meth}`wsgi_tools.filtered_parser.Options` allows the value.

- {py:meth}`wsgi_tools.filtered_parser.List` has to be constructed with another filter. If this filter allows every value in the list, the {py:meth}`wsgi_tools.filtered_parser.List` allows the list.

- {py:meth}`wsgi_tools.filtered_parser.Object` has to be constructed with a dict of this shape:

  ```python
  {
      "key1": filter1,
      "key2": (filter2, True)
  }
  ```

  In this example, the object has to have a key `"key1"` and it's value has to be allowed by `filter1`. The key `"key2"` is optinal, because it is in a tuple with `True` as the second value. If `"key2"` exists, it's value has to be allowed by `filter2`. Otherwies {py:meth}`wsgi_tools.filtered_parser.Object` won't allow this json-object.
