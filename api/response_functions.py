
class Response:

    @staticmethod
    def get_error_status(err_id, error_lookup):
        return {
            'status': 'error',
            'info': {
                'error_id': err_id,
                'error_text': error_lookup[err_id]
            }
        }

    @staticmethod
    def get_success_status():
        return {
            'status': 'success'
        }
