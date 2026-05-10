"""Centralized, environment-variable-backed configuration.

All credentials and provider URLs are read from the process environment so
secrets never end up in source control or log files. A `.env` file in the
working directory is auto-loaded if present.
"""

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class IBMQuantumSettings(BaseSettings):
    """Credentials for IBM Quantum (via qiskit-ibm-runtime)."""

    model_config = SettingsConfigDict(
        env_prefix="IBM_QUANTUM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    token: SecretStr | None = Field(default=None, description="IBM Quantum API token.")
    instance: str | None = Field(
        default=None,
        description="Hub/group/project, e.g. 'ibm-q/open/main'.",
    )
    channel: str = Field(
        default="ibm_quantum",
        description="Runtime channel: 'ibm_quantum' or 'ibm_cloud'.",
    )


class BraketSettings(BaseSettings):
    """Credentials for Amazon Braket (uses standard AWS env vars)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    aws_access_key_id: SecretStr | None = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: SecretStr | None = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: SecretStr | None = Field(default=None, alias="AWS_SESSION_TOKEN")
    aws_region: str | None = Field(default=None, alias="AWS_DEFAULT_REGION")
    s3_bucket: str | None = Field(default=None, alias="AWS_BRAKET_S3_BUCKET")
    s3_prefix: str | None = Field(default=None, alias="AWS_BRAKET_S3_PREFIX")


class OqtopusSettings(BaseSettings):
    """Credentials for OQTOPUS Cloud."""

    model_config = SettingsConfigDict(
        env_prefix="OQTOPUS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_token: SecretStr | None = Field(default=None)
    api_url: str | None = Field(default=None)


__all__ = ["BraketSettings", "IBMQuantumSettings", "OqtopusSettings"]
