class TokenizerException(Exception):
    """Exception raised for issues during Tokenization"""
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token
    
    def __str__():
        return f"TokenizerException: {self.message} on token '{self.token}'"
    
