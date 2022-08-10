from cv.run_cv import main
import time
import sys

if __name__ == '__main__':

    start_time = time.time()

    doc_path = None
    debug_mode = False
    for i in range(len(sys.argv)):
        if sys.argv[i] == '--file':
            doc_path = sys.argv[i + 1]
        if sys.argv[i] == '--debug':
            debug_mode = True
    if doc_path is None:
        print('Error: enter doc path\npython main.py --file myfile.pdf')
    else:
        result = main(doc_path, debug_mode)
        if debug_mode != True: 
            print(f'''Результат:\n
            Страницы с объемом меньше 70%:  {result['pages_with_text_size_failure']}\n
            Проверка подписи:               {result['signature_check']}\n
            Проверка печати:                {result['printing_check']}\n
            \n''')
        print(f"--- Executed for {(time.time() - start_time):.3f}s seconds ---")
    