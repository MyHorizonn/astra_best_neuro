## Создание и активация виртуального окружения
#### Linux/MacOS
```
python3 -m venv env
source env/bin/activate
pip install -r req.txt
```
#### Windows
```
python3 -m venv env
env\Scripts\activate
pip install -r req.txt
```
## Запуск сервера
```
python run.py
```

## Тестирование обработки файла
Для вывода картинок добавить --debug
```
python test_cv.py --file myfile.pdf
```
Пример вывода:
```
Результат:

            Страницы с объемом меньше 70%:  [1, 2, 3, 4, 5, 6, 7]

            Проверка подписи:               True

            Проверка печати:                True

```
