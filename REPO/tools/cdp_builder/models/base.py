"""Base classes for constitutive models."""
from enum import Enum


class ModelStatus(Enum):
    IMPLEMENTED_REFERENCE = "IMPLEMENTED_REFERENCE"  # not a named C/T model
    IMPLEMENTED = "IMPLEMENTED"                       # verified from source paper
    REVIEW_REQUIRED = "REVIEW_REQUIRED"               # source paper not in 01_SOURCES


class ModelNotAvailableError(RuntimeError):
    """Raised when a REVIEW_REQUIRED model is invoked."""


class BaseModel:
    MODEL_ID = "BASE"
    STATUS = ModelStatus.REVIEW_REQUIRED
    SOURCE_PAPER = "UNKNOWN"

    def generate_table(self, **kwargs):
        if self.STATUS == ModelStatus.REVIEW_REQUIRED:
            raise ModelNotAvailableError(
                f"Model {self.MODEL_ID} is REVIEW_REQUIRED: "
                f"source paper '{self.SOURCE_PAPER}' not found in "
                "01_SOURCES/02_SECONDARY_REFERENCE. "
                "Add the paper and implement the equations before calling."
            )
        raise NotImplementedError(f"{self.MODEL_ID}.generate_table()")
