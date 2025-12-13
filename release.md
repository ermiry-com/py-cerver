# Create PyCerver Release

0. Update the version in `cerver/version.py` (with its date and time) and in `version.txt`, the changes of the
release in `CHANGELOG.md`, and its breaking changes in `incompatibilities.md`

1. Run every tier against the cerver of the release, normal and with the sanitizers

```
CERVER_DIR=/path/to/cerver ./tests/build.sh
SANITIZER=address,undefined CERVER_DIR=/path/to/cerver ./tests/build.sh
./tests/run.sh
./tests/run.sh asan
```

2. Build, from a clean tree

```
rm -rf build dist
python3 -m build
```

3. Upload

```
python3 -m twine upload dist/*
```
