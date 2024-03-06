class InsufficientBalanceException(Exception):
    """
    Exception raised when a user tries to accept a request but does not have enough balance.
    """
    def __init__(self, message="Insufficient balance to complete the transaction"):
        self.message = message
        super().__init__(self.message)