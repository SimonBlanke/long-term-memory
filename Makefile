dist:
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install:
	pip install .

develop:
	pip install -e .

reinstall:
	pip uninstall -y long_term_memory
	rm -fr build dist long_term_memory.egg-info
	python setup.py bdist_wheel
	pip install dist/*


test:
	pytest -p no:warnings -rfEX tests/ \
