import os
from pathlib import Path


def _first_existing_path(paths):
    for path in paths:
        if path.exists():
            return path
    return None


def _candidate_roots(module_dir, model_dir):
    candidates = []

    for raw_value in (
        model_dir,
        os.environ.get('DICE_GAME_MODEL_DIR'),
        os.environ.get('DICE_GAME_ROOT'),
    ):
        if raw_value:
            candidates.append(Path(raw_value).expanduser().resolve())

    current = Path(module_dir).resolve()
    candidates.extend(current.parents)

    unique_candidates = []
    seen = set()
    for candidate in candidates:
        candidate_str = str(candidate)
        if candidate_str not in seen:
            seen.add(candidate_str)
            unique_candidates.append(candidate)
    return unique_candidates


def resolve_model_paths(module_dir, model_dir='', yolo_model_path='', keras_model_path=''):
    explicit_yolo = Path(yolo_model_path).expanduser().resolve() if yolo_model_path else None
    explicit_keras = Path(keras_model_path).expanduser().resolve() if keras_model_path else None

    if explicit_yolo and not explicit_yolo.exists():
        raise FileNotFoundError(f'YOLO model not found: {explicit_yolo}')
    if explicit_keras and not explicit_keras.exists():
        raise FileNotFoundError(f'Keras model not found: {explicit_keras}')

    if explicit_yolo and explicit_keras:
        return str(explicit_yolo), str(explicit_keras)

    roots = _candidate_roots(module_dir, model_dir)
    model_roots = []

    for root in roots:
        if root.name == 'models':
            model_roots.append(root)
        model_roots.append(root / 'models')

    unique_model_roots = []
    seen_model_roots = set()
    for model_root in model_roots:
        model_root_str = str(model_root)
        if model_root_str not in seen_model_roots:
            seen_model_roots.add(model_root_str)
            unique_model_roots.append(model_root)

    yolo_candidates = []
    keras_candidates = []

    for root in unique_model_roots:
        yolo_candidates.extend([
            root / 'yolov8n.pt',
        ])
        keras_candidates.extend([
            root / 'green_dice_model.keras',
        ])

    resolved_yolo = explicit_yolo or _first_existing_path(yolo_candidates)
    resolved_keras = explicit_keras or _first_existing_path(keras_candidates)

    if resolved_yolo is None or resolved_keras is None:
        raise FileNotFoundError(
            'Could not resolve model files from a models directory. '
            'Set model_dir to a models directory, set explicit model paths, '
            'or export DICE_GAME_MODEL_DIR.'
        )

    return str(resolved_yolo), str(resolved_keras)
