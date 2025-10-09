"""Configuration loader utility."""

import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration management class."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Load configuration from YAML file."""
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key path."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)

    @property
    def database_path(self) -> str:
        """Get database path."""
        return self.get('database.path', 'database/onelead.db')

    @property
    def install_base_path(self) -> str:
        """Get install base data source path."""
        return self.get('data_sources.install_base')

    @property
    def service_sku_path(self) -> str:
        """Get service SKU data source path."""
        return self.get('data_sources.service_sku')


# Global configuration instance
config = Config()
