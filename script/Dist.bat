set /p TOKEN=<nodistribute/TOKEN
python -m twine upload -u __token__ -p %TOKEN% dist/*