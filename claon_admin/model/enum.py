from enum import Enum


class Role(Enum):
    USER = "user"
    LECTOR = "lector"
    CENTER_ADMIN = "center_admin"


class SignUpRole(Enum):
    LECTOR = "lector"
    CENTER_ADMIN = "center_admin"


class OAuthProvider(Enum):
    GOOGLE = "google"
    KAKAO = "kakao"


class CenterUploadPurpose(Enum):
    PROFILE = "profile"
    IMAGE = "image"
    FEE = "fee"
    PROOF = "proof"


class WallType(Enum):
    ENDURANCE = "endurance"
    BOULDERING = "bouldering"