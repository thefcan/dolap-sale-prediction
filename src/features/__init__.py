"""Feature engineering public API."""

__all__ = ["FeatureEngineer"]


def __getattr__(name: str):
	if name == "FeatureEngineer":
		from src.features.engineer import FeatureEngineer

		return FeatureEngineer
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
