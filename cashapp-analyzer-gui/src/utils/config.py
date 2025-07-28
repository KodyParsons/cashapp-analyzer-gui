"""Configuration management for Cash App Analyzer"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
import os
import tempfile

@dataclass
class AppConfig:
    """Application configuration settings"""
    # GUI Settings
    window_width: int = 1000
    window_height: int = 700
    window_title: str = "Cash App Transaction Analyzer"
    
    # Analysis Settings
    default_date_range_months: int = 6
    max_transactions_display: int = 1000
      # Visualization Settings
    chart_dpi: int = 150
    chart_figure_size: tuple = (16, 12)
    pdf_chart_width: float = 6.0  # inches (reduced from 8.0)
    pdf_chart_height: float = 4.5  # inches (reduced from 10.0)
    
    # File Settings
    temp_dir: Optional[str] = None
    default_export_format: str = "pdf"
    
    # PDF Settings
    pdf_page_size: str = "letter"
    pdf_font_size: int = 10
    pdf_title_font_size: int = 16
    
    def __post_init__(self):
        """Initialize computed properties"""
        if self.temp_dir is None:
            self.temp_dir = tempfile.gettempdir()
    
    @classmethod
    def load(cls, config_path: str = "config.json") -> 'AppConfig':
        """Load configuration from file"""
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_dict = json.load(f)
                return cls(**config_dict)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not load config file: {e}")
                return cls()
        return cls()
    
    def save(self, config_path: str = "config.json") -> None:
        """Save configuration to file"""
        try:
            # Convert dataclass to dict, handling tuples
            config_dict = {}
            for key, value in self.__dict__.items():
                if isinstance(value, tuple):
                    config_dict[key] = list(value)
                else:
                    config_dict[key] = value
            
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get_temp_file_path(self, filename: str) -> str:
        """Get a temporary file path"""
        return os.path.join(self.temp_dir, filename)


# Global config instance
config = AppConfig.load()
