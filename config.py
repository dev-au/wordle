from fastapi.templating import Jinja2Templates

template = Jinja2Templates('templates')
DB_URL = 'sqlite://db.sqlite3'

word_data = {
    'css': 2,
    'html': 5,
    'python': 2,
    'javascript': 1,
    'assembly': 3,
    'java': 3,
    'swift': 5,
    'pascal': 5,
    'ada': 3,
    'fortan': 7,
}

