class UnreadableDataError(ValueError):
    """Exception raised when the data cannot be read by the schema."""


class ResolutionError(ValueError):
    """Exception raised when the schema cannot be resolved."""


class UnhandledKeyError(ValueError):
    """Exception raised when an unhandled key is encountered in the schema."""


class NoSchemaIdError(KeyError):
    """Exception raised when a schema does not have an ID."""

    def __init__(self) -> None:
        super().__init__("Schema must have an 'id' attribute, which is not None.")


class SchemaIdExistsError(KeyError):
    """Exception raised when a schema address already exists in the manager."""

    def __init__(self, uri: str) -> None:
        super().__init__(f"Schema with uri '{uri}' already exists.")
        self.uri = uri


class NoSchemaDefinitionsError(KeyError):
    """Exception raised when a schema does not have definitions."""

    def __init__(self, uri: str) -> None:
        super().__init__(f"Schema '{uri}' has no definitions.")
        self.uri = uri
