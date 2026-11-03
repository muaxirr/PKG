import webview

if __name__ == '__main__':
    # Создаем окно приложения, загружающее ваш HTML-файл
    webview.create_window('Конвертер Цветовых Моделей', 'index.html', width=1200, height=800)
    webview.start()