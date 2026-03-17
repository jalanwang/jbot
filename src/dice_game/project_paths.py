from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
MODELS_DIR = ROOT_DIR / 'models'
DATASETS_DIR = ROOT_DIR / 'datasets'
DATA_DIR = DATASETS_DIR / 'processed' / 'classified'
TEST_IMAGES_DIR = ROOT_DIR / 'test_images'
CAPTURES_DIR = DATASETS_DIR / 'captures'
PROCESSED_DIR = DATASETS_DIR / 'processed'
RAW_DIR = DATASETS_DIR / 'raw'

CAPTURED_IMAGES_DIR = CAPTURES_DIR / 'images'
REALTIME_INPUT_DIR = CAPTURES_DIR / 'realtime_input'
PREPROCESSED_IMAGES_DIR = PROCESSED_DIR / 'images'
PREPROCESSED_DIR = PROCESSED_DIR / 'base'
PREPROCESSED_RT_DIR = PROCESSED_DIR / 'realtime'
RAW_GREEN_DATA_DIR = RAW_DIR / 'green_dice'
RAW_IRIUN_DATA_DIR = RAW_DIR / 'irin'
CLASSIFIED_DATA_DIR = PROCESSED_DIR / 'classified'
NOTEBOOKS_OR_TRAINING_DIR = ROOT_DIR / 'notebooks_or_training'
WORKFLOW_DIR = ROOT_DIR / 'workflow'


def _candidate_files(name):
    return [
        MODELS_DIR / name,
    ]


def resolve_model_file(name):
    for candidate in _candidate_files(name):
        if candidate.exists():
            return candidate
    return _candidate_files(name)[0]
