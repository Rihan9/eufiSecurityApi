rmdir /s /Q build
rmdir /s /Q dist
rmdir /s /Q eufy_security_api_rihan.egg-info
python setup.py build
python setup.py sdist bdist_wheel