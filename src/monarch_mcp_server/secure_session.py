"""
Secure session management for Monarch Money MCP Server using environment variables.
"""

import logging
import os
from typing import Optional
from pathlib import Path
from monarchmoney import MonarchMoney

logger = logging.getLogger(__name__)

# Environment variable for token storage
MONARCH_TOKEN_ENV_VAR = "MONARCH_TOKEN"
ENV_FILE_PATH = Path(__file__).parent.parent.parent / ".env"


class SecureMonarchSession:
    """Manages Monarch Money sessions securely using environment variables."""

    def save_token(self, token: str) -> None:
        """Save the authentication token to the .env file."""
        try:
            # Read existing .env file content
            env_content = {}
            if ENV_FILE_PATH.exists():
                with open(ENV_FILE_PATH, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key] = value

            # Update or add the MONARCH_TOKEN
            env_content[MONARCH_TOKEN_ENV_VAR] = token

            # Write back to .env file
            with open(ENV_FILE_PATH, 'w') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")

            logger.info("✅ Token saved securely to .env file")

            # Clean up any old insecure files
            self._cleanup_old_session_files()

        except Exception as e:
            logger.error(f"❌ Failed to save token to .env file: {e}")
            raise

    def load_token(self) -> Optional[str]:
        """Load the authentication token from environment variables."""
        try:
            token = os.getenv(MONARCH_TOKEN_ENV_VAR)
            if token:
                logger.info("✅ Token loaded from environment variable")
                return token
            else:
                logger.info("🔍 No token found in environment variables")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to load token from environment: {e}")
            return None

    def delete_token(self) -> None:
        """Delete the authentication token from the .env file."""
        try:
            # Read existing .env file content
            env_content = {}
            if ENV_FILE_PATH.exists():
                with open(ENV_FILE_PATH, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key] = value

            # Remove the MONARCH_TOKEN if it exists
            if MONARCH_TOKEN_ENV_VAR in env_content:
                del env_content[MONARCH_TOKEN_ENV_VAR]

                # Write back to .env file
                with open(ENV_FILE_PATH, 'w') as f:
                    for key, value in env_content.items():
                        f.write(f"{key}={value}\n")

                logger.info("🗑️ Token deleted from .env file")
            else:
                logger.info("🔍 No token found in .env file to delete")

            # Also clean up any old insecure files
            self._cleanup_old_session_files()

        except Exception as e:
            logger.error(f"❌ Failed to delete token from .env file: {e}")

    def get_authenticated_client(self) -> Optional[MonarchMoney]:
        """Get an authenticated MonarchMoney client."""
        token = self.load_token()
        if not token:
            return None

        try:
            client = MonarchMoney(token=token)
            logger.info("✅ MonarchMoney client created with stored token")
            return client
        except Exception as e:
            logger.error(f"❌ Failed to create MonarchMoney client: {e}")
            return None

    def save_authenticated_session(self, mm: MonarchMoney) -> None:
        """Save the session from an authenticated MonarchMoney instance."""
        if mm.token:
            self.save_token(mm.token)
        else:
            logger.warning("⚠️  MonarchMoney instance has no token to save")

    def _cleanup_old_session_files(self) -> None:
        """Clean up old insecure session files."""
        cleanup_paths = [
            ".mm/mm_session.pickle",
            "monarch_session.json",
            ".mm",  # Remove the entire directory if empty
        ]

        for path in cleanup_paths:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        os.remove(path)
                        logger.info(f"🗑️ Cleaned up old insecure session file: {path}")
                    elif os.path.isdir(path) and not os.listdir(path):
                        os.rmdir(path)
                        logger.info(f"🗑️ Cleaned up empty session directory: {path}")
            except Exception as e:
                logger.warning(f"⚠️  Could not clean up {path}: {e}")


# Global session manager instance
secure_session = SecureMonarchSession()
