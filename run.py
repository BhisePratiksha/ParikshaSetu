import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    print("\n" + "=" * 56)
    print("ParikshaSetu Government Exam Preparation Platform")
    print(f"Server running at: http://{host}:{port}/")
    print("Admin login: admin@parikshasetu.com / Admin@123")
    print("Student login: student@parikshasetu.com / Student@123")
    print("=" * 56 + "\n")
    app.run(host=host, port=port, debug=debug)
