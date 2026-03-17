import os
import sys
import importlib.util

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DETECTOR_ENTRYPOINT = os.path.join(
    CURRENT_DIR,
    'ros2',
    'dice_detector_pkg',
    'dice_detector_pkg',
    'detector_node.py',
)


def main(args=None):
    spec = importlib.util.spec_from_file_location('dice_detector_entrypoint', DETECTOR_ENTRYPOINT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Failed to load detector entrypoint: {DETECTOR_ENTRYPOINT}')

    module = importlib.util.module_from_spec(spec)
    sys.modules['dice_detector_entrypoint'] = module
    spec.loader.exec_module(module)
    module.main(args=args)

if __name__ == '__main__':
    main()
