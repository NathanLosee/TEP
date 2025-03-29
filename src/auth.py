import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from jwt import JWT, AbstractJWKBase, jwk_from_pem
from src.constants import HTTPMethod, ResourceType

rsa_private_key: rsa.RSAPrivateKey = None
rsa_public_key: rsa.RSAPublicKey = None
signing_key: AbstractJWKBase = None
verifying_key: AbstractJWKBase = None

jwt_instance = JWT()


def load_keys():
    """Load the RSA private and public keys from local file."""
    global rsa_private_key, rsa_public_key, signing_key, verifying_key

    if not os.path.exists("rsa_private_key.pem"):
        rsa_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        with open("rsa_private_key.pem", "wb") as private_key_file:
            private_key_file.write(
                rsa_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
    else:
        with open("rsa_private_key.pem", "rb") as private_key_file:
            rsa_private_key = serialization.load_pem_private_key(
                private_key_file.read(), password=None
            )

    rsa_public_key = rsa_private_key.public_key()

    signing_key = jwk_from_pem(
        rsa_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    verifying_key = jwk_from_pem(
        rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def hash_value(value: str) -> str:
    """Hash the provided value.

    Args:
        value (str): The value to hash.

    Returns:
        str: The hashed value.

    """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(value)

    return digest.finalize()


def encode_jwt_token(payload: dict) -> str:
    """Encode the provided payload into a JWT token.

    Args:
        payload (dict): The payload to encode.

    Returns:
        str: The JWT token.

    """
    return jwt_instance.encode(payload, signing_key, alg="RS256")


def decode_jwt_token(jwt: str) -> dict:
    """Decode the provided JWT token.

    Args:
        jwt (str): The JWT token to decode.

    Returns:
        dict: The decoded payload.

    """
    return jwt_instance.decode(jwt, verifying_key, algorithms=["RS256"])


def requires_permission(
    jwt: str, method: HTTPMethod, resource: ResourceType
) -> bool:
    """Check if the JWT token has the required permission.

    Args:
        jwt (str): The JWT token to check.
        method (HTTPMethod): The HTTP method to check.
        resource (ResourceType): The resource to check.

    Returns:
        bool: True if the JWT token has the required permission.

    """
    payload = decode_jwt_token(jwt)
    has_permission = False
    for permission in payload["permissions"]:
        if (
            permission["http_method"] == method
            and permission["resource"] == resource
        ):
            has_permission = True
            break
    return has_permission
