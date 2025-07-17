class GlobalExceptionHandler:
    def __init__(self) -> None:
        pass

    def register_error_handler(self, error_type, handler):
        pass

    def handle_exception_sync(self, exception):
        return {"handled": True}