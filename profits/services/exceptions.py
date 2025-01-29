class ServiceException(Exception):
    """Base exception for all service layer exceptions"""
    pass

class CurrencyRepositoryException(ServiceException):
    """Base exception for currency service specific exceptions"""
    pass

class CurrencyConversionException(CurrencyRepositoryException):
    """Raised when there's an error in currency conversion"""
    pass

class CurrencyExchangeNotFoundException(CurrencyRepositoryException):
    """Raised when a required exchange rate is not found"""
    pass

class ProfitServiceBuySellMissmatch(ServiceException):
    """Raised when a required there are more stocks sold that bought"""
    pass
