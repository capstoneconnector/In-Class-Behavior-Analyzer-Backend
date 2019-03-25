
class Response:

    @staticmethod
    def get_error_status(error_id, error_lookup):
        """
            Function Summary: This static function is used to get an error status for API returns.

            Args:
                error_id -- The ID of the error
                error_lookup -- The dictionary to lookup the error ID

            Return:
                Type: dict
                Data: A dictionary containing information about the error
        """
        return {
            'status': 'error',
            'info': {
                'error_id': error_id,
                'error_text': error_lookup[error_id]
            }
        }

    @staticmethod
    def get_success_status():
        """
            Function Summary: This static function is used to get an success status for API returns.

            Args:

            Return:
                Type: dict
                Data: A dictionary containing success information
        """
        return {
            'status': 'success'
        }
