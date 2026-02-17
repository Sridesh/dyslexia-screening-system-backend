# app/ef_ads/__init__.py

"""
EF-ADS (Entropy–Fatigue Adaptive Dyslexia Screening) core package.

This package contains all domain logic for:
- Bayesian ability estimation per module
- Response time and fatigue modeling
- Entropy-based item selection
- Stopping rules
- Risk classification and explanations

It must not import FastAPI, SQLAlchemy, or any HTTP/DB specific code.
"""

from . import config
from .state import SessionState
