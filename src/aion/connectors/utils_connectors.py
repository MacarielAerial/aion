from pydantic import BaseModel


class AWSCredentials(BaseModel):
    access_key_id: str
    secret_access_key: str
    session_token: str
