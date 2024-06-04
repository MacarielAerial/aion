import hashlib
import uuid
from typing import IO, Tuple


def generate_uuid_from_file(file: IO) -> uuid.UUID:
    # Compute the hash of the file content
    hasher = hashlib.sha256()

    # Read the file in chunks to handle large files efficiently
    for chunk in iter(lambda: file.read(4096), b""):
        hasher.update(chunk)

    # Get the hexadecimal digest of the hash
    file_hash = hasher.hexdigest()

    # Generate the UUID using uuid5 with the hash as the name
    file_uuid = uuid.uuid5(uuid.NAMESPACE_URL, file_hash)

    return file_uuid


def generate_uuid_from_uuid_xyz(
    existing_uuid: uuid.UUID, int_tuple: Tuple[int, int, int]
) -> uuid.UUID:
    # Convert the UUID to a string
    uuid_str = str(existing_uuid)

    # Convert the tuple of integers to a string
    tuple_str = f"{int_tuple[0]},{int_tuple[1]},{int_tuple[2]}"

    # Combine the UUID string and the integer tuple string
    combined_str = f"{uuid_str}-{tuple_str}"

    # Generate the new UUID using uuid5
    new_uuid = uuid.uuid5(uuid.NAMESPACE_URL, combined_str)

    return new_uuid
