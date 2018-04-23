# pylint:disable=line-too-long

""" Exceptions for sshpubkeys """


class InvalidKeyException(Exception):
    """ Invalid key - something is wrong with the key, and it should not be accepted, as OpenSSH will not work with it. """
    pass


class InvalidKeyLengthException(InvalidKeyException):
    """ Invalid key length - either too short or too long.

    See also TooShortKeyException and TooLongKeyException """
    pass


class TooShortKeyException(InvalidKeyLengthException):
    """ Key is shorter than what the specification allows """
    pass


class TooLongKeyException(InvalidKeyLengthException):
    """ Key is longer than what the specification allows """
    pass


class InvalidTypeException(InvalidKeyException):
    """ Key type is invalid or unrecognized """
    pass


class MalformedDataException(InvalidKeyException):
    """ The key is invalid - unable to parse the data. The data may be corrupted, truncated, or includes extra content that is not allowed. """
    pass


class InvalidOptionsException(MalformedDataException):
    """ Options string is invalid: it contains invalid characters, unrecognized options, or is otherwise malformed. """
    pass


class InvalidOptionNameException(InvalidOptionsException):
    """ Invalid option name (contains disallowed characters, or is unrecognized.) """
    pass


class UnknownOptionNameException(InvalidOptionsException):
    """ Unrecognized option name. """
    pass


class MissingMandatoryOptionValueException(InvalidOptionsException):
    """ Mandatory option value is missing. """
    pass
