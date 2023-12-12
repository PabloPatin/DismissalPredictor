from datetime import time
import os

WORKERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'workers.csv')
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'test_data.csv')

MIN_MESSAGE_LEN = 10
DEVIATION_MODIFIER = 0.6

WORK_DAY_START = time(11, 0, 0)
WORK_DAY_END = time(19, 0, 0)