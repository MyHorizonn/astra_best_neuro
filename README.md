### Создание виртуального окружения
```
python3 -m venv lenv
source env/bin/activate
pip install -r req.txt
```

### Тестирование 
```
python main.py --file myfile.pdf
```
Пример вывода:
```
{'pages_with_text_size_failure': [1, 2, 3, 4, 5], 'signature_check': True}
```