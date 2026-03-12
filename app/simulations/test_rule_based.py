import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.adaptive_testing_module import config
config.ML_MODEL_TYPE = "rule_based"
config.RISK_SCORE_HIGH = 0.60
config.RISK_SCORE_MODERATE = 0.40
import app.simulations.master_validation_suite as mvs
mvs.main()
