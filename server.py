import http.server
import socketserver
import webbrowser
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    PORT = 8000
    
    # Если мы в распакованном exe, файлы будут в sys._MEIPASS
    # Иначе - в текущей директории
    web_dir = resource_path(".")
    
    print(f"Запуск сервера из директории: {web_dir}")
    print(f"Файлы в директории: {os.listdir(web_dir) if os.path.exists(web_dir) else 'директория не найдена'}")
    
    os.chdir(web_dir)
    
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\nСервер запущен на http://localhost:{PORT}")
        print("Открываю браузер...")
        webbrowser.open(f"http://localhost:{PORT}")
        print("Нажмите Ctrl+C для остановки сервера\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")

if __name__ == "__main__":
    main()