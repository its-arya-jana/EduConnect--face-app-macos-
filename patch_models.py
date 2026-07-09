#!/usr/bin/env python3
"""Patch face_recognition_models to work with Python 3.14+ (no pkg_resources)."""
import os
import sys
import shutil

# Find the face_recognition_models package
paths = [
    os.path.join(os.path.dirname(sys.executable), '..', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages', 'face_recognition_models'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages', 'face_recognition_models'),
]

init_path = None
for p in paths:
    candidate = os.path.abspath(os.path.join(p, '__init__.py'))
    if os.path.exists(candidate):
        init_path = candidate
        break

if not init_path:
    # Try to locate via import
    try:
        import face_recognition_models
        init_path = os.path.join(os.path.dirname(face_recognition_models.__file__), '__init__.py')
    except ImportError:
        pass

if not init_path or not os.path.exists(init_path):
    print("face_recognition_models not found — skipping patch")
    sys.exit(0)

with open(init_path) as f:
    content = f.read()

if 'importlib.resources' in content:
    print("Already patched")
    sys.exit(0)

# First try: replace pkg_resources with importlib.resources
backup = init_path + '.bak'
shutil.copy2(init_path, backup)
print(f"Patched {init_path}")

new_content = content.replace(
    "from pkg_resources import resource_filename",
    "try:\n    from pkg_resources import resource_filename\nexcept ImportError:\n    from importlib.resources import files as _files\n    def resource_filename(pkg, path): return str(_files(pkg) / path)"
)

with open(init_path, 'w') as f:
    f.write(new_content)

# Verify
try:
    import face_recognition_models
    print("Patch verified: face_recognition_models imports OK")
except Exception as e:
    print(f"Patch failed: {e}")
    shutil.copy2(backup, init_path)
    os.remove(backup)
    sys.exit(1)

if os.path.exists(backup):
    os.remove(backup)
