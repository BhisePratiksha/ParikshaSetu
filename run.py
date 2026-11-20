import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 in production (Render), 127.0.0.1 locally
    is_production = os.environ.get('FLASK_ENV', 'development') == 'production'
    host = '0.0.0.0' if is_production else os.environ.get('HOST', '127.0.0.1')
    debug = not is_production and os.environ.get('FLASK_DEBUG', '1') == '1'
    if not is_production:
        print("\n" + "=" * 56)
        print("ParikshaSetu Government Exam Preparation Platform")
        print(f"Server running at: http://{host}:{port}/")
        print("Admin login: admin@parikshasetu.com / Admin@123")
        print("Student login: student@parikshasetu.com / Student@123")
        print("=" * 56 + "\n")
    app.run(host=host, port=port, debug=debug)
