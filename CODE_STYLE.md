# Function Comments
### Description
```python
"""
    (REQUIRED) Function Summary: A detailed explanation of the purpose of the function and what role it plays in the project.
    (OPTIONAL) Path: 'path/to/get/to/function'
    (OPTIONAL) Request Type: POST

    (REQUIRED) Args: - A list of the arguments passed to the function. Should still exist even if there are no arguments.
        arg -- Argument explanation

    (OPTIONAL) Required GET Parameters:
        get_parameter -- Parameter explanation
        
    (OPTIONAL) Required POST parameters:
        post_parameter -- Parameter explanation

    (REQUIRED) Return: - The return type and data that should be returned
        Type: type
        Data: Explanation of the data
"""
```

### Template
```python
"""
    Function Summary: 
    Path: ''
    Request Type: GET

    Args:
        arg -- Argument explanation

    Required GET Parameters:
        get_parameter -- Parameter explanation
        
    Required POST parameters:
        post_parameter -- Parameter explanation

    Return:
        Type: 
        Data:
"""
```

# Status from API
### Success Status
The success status is returned when the API call was completed successfully. The data object will only exist in functions
require some data to be returned.
```json
{
  "status": "success",
  "data": {}
}
```
### Error Status
The error status is returned when the API call failed to complete.
```json
{
  "status": "error",
  "info": {
    "error_id": 100,
    "error_text": "No session_id in parameters of url"
  }
}
```