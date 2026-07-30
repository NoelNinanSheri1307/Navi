"""
loader.py
---------
Thread-safe dataset ingestion and validation module for Navi framework.

Encapsulates dataset loading, column verification, missing values calculation,
and min/max statistics calculation for VANET telemetry CSV files.
"""

import os
import threading
from typing import Dict, Any, Optional
import pandas as pd
from fuzzy.fuzzy_system import set_dataset_stats


class DatasetLoader:
    """
    Thread-safe singleton/cached loader for VANET telemetry dataset files.

    Attributes
    ----------
    csv_path : str
        Target CSV filepath.
    """

    _instance_lock = threading.Lock()
    _cached_df: Optional[pd.DataFrame] = None
    _cached_stats: Dict[str, float] = {}
    _current_path: Optional[str] = None

    @classmethod
    def load_dataset(cls, csv_path: str = "vanet.csv") -> pd.DataFrame:
        """
        Load, validate, and cache the target dataset dataframe.

        Parameters
        ----------
        csv_path : str
            Path to dataset CSV file.

        Returns
        -------
        pd.DataFrame
            Validated dataset dataframe.
        """
        with cls._instance_lock:
            # Resolve the dataset path absolutely relative to the module structure
            datasets_module_dir = os.path.dirname(os.path.abspath(__file__))  # backend/datasets/
            project_root_dir = os.path.dirname(os.path.dirname(datasets_module_dir))  # Navi/

            possible_paths = [
                os.path.abspath(csv_path),
                os.path.join(datasets_module_dir, csv_path),
                os.path.join(project_root_dir, csv_path),
            ]

            resolved_path = None
            for p in possible_paths:
                if os.path.isfile(p):
                    resolved_path = p
                    break

            if not resolved_path:
                checked = ", ".join(f"'{p}'" for p in possible_paths)
                raise FileNotFoundError(
                    f"VANET dataset file '{csv_path}' could not be resolved. Checked: {checked}"
                )

            abs_path = resolved_path

            if cls._cached_df is not None and cls._current_path == abs_path:
                return cls._cached_df

            df = pd.read_csv(abs_path, sep=",", engine="python")

            # Compute congestion_pressure if missing from raw telemetry
            if "congestion_pressure" not in df.columns:
                df["congestion_pressure"] = (df["density_veh_per_km"] / 120.0) * (
                    df["avg_wait_time_s"] / 60.0
                )

            required_cols = {
                "congestion_pressure",
                "density_veh_per_km",
                "queue_length_veh",
                "avg_wait_time_s",
                "flow_veh_per_hr",
            }
            missing = required_cols - set(df.columns)
            if missing:
                raise ValueError(f"Dataset '{abs_path}' missing columns: {missing}")

            stats = {
                "cp_min": float(df["congestion_pressure"].min()),
                "cp_max": float(df["congestion_pressure"].max()),
                "den_min": float(df["density_veh_per_km"].min()),
                "den_max": float(df["density_veh_per_km"].max()),
                "que_min": float(df["queue_length_veh"].min()),
                "que_max": float(df["queue_length_veh"].max()),
                "wt_min": float(df["avg_wait_time_s"].min()),
                "wt_max": float(df["avg_wait_time_s"].max()),
                "fl_min": float(df["flow_veh_per_hr"].min()),
                "fl_max": float(df["flow_veh_per_hr"].max()),
            }

            cls._cached_df = df
            cls._cached_stats = stats
            cls._current_path = abs_path
            
            # Pass stats to fuzzy system context
            set_dataset_stats(stats)

            return df

    @classmethod
    def get_stats(cls, csv_path: str = "vanet.csv") -> Dict[str, float]:
        """Load dataset and return min/max statistics dictionary."""
        cls.load_dataset(csv_path)
        return cls._cached_stats.copy()

    @classmethod
    def clear_cache(cls) -> None:
        """Reset cached dataframe and statistics objects."""
        with cls._instance_lock:
            cls._cached_df = None
            cls._cached_stats = {}
            cls._current_path = None
