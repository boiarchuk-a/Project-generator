from auth import auth_settings
from Admin import Admin

def test_user_creation_with_correct_data(test_client, db_session):
    """Проверим, что регистрация пользователя с корректными данными проходит успешно"""
    users_manager = Admin(db_session)
    # Первый test_user создается в фикстуре, поэтому здесь test_user_2
    user_data = {
        "username": "test_user_2",
        "password": "qwerty123",
        "email": "test_user_2@gmail.com",
        "fullname": "Test User #2",
    }
    response = test_client.post("/user/signup", json=user_data)
    assert response.status_code == 201
    # Проверим, что пользователь действительно в БД, для этого вызовем метод signin().
    # Если пользователя не окажется, произойдет исключение и тест будет провален
    users_manager.signin(username="test_user", password="qwerty123")

def test_user_creation_with_incorrect_username(test_client):
    """Проверим, что регистрация пользователя с некорректными именем пользователя
    не проходит"""
    incorrect_usernames = [
        "aa", # Меньше 3 символов
        "aa?", "aa.bb", # Недопустимые символы
        "test_user" # Повтор имени (создан в фикстуре)
    ]
    for incorrect_username in incorrect_usernames:
        user_data = {
            "username": incorrect_username,
            "password": "qwerty123",
            "email": "_____@gmail.com",
        }
        response = test_client.post("/user/signup", json=user_data)
        assert response.status_code == 400

def test_user_creation_with_incorrect_password(test_client):
    """Проверим, что регистрация пользователя с некорректными паролем не проходит"""
    incorrect_password = "1234567" # Меньше 8 символов
    user_data = {
        # Первый test_user создается в фикстуре, поэтому здесь test_user_2
        "username": "test_user_2",
        "password": incorrect_password,
        "email": "test_user_2@gmail.com",
    }
    response = test_client.post("/user/signup", json=user_data)
    assert response.status_code == 400

def test_user_creation_with_incorrect_email(test_client):
    """Проверим, что регистрация пользователя с некорректными адресом электронной почты
    не проходит"""
    incorrect_emails = [
        "",
        "gmail",
        "gmail.com",
        "@gmail.com",
        "test_user",
        "test_user@",
        "test_user@gmail",
        "test_user.gmail.com",
    ]
    for incorrect_email in incorrect_emails:
        user_data = {
            "username": "test_user_2",
            "password": "qwerty123",
            "email": incorrect_email,
        }
        response = test_client.post("/user/signup", json=user_data)
        assert response.status_code == 400

def test_user_signin(test_client):
    """Проверим, что вход пользователя работает корректно"""
    # Пользователь с такими параметрами создан в фикистуре test_user,
    # которая вызывается test_client
    user_data = {
        "username": "test_user",
        "password": "qwerty123"
    }
    response = test_client.post("/user/signin", json=user_data)
    # Если все нормально, будет присвоен токен. Если же токена не окажется,
    # здесь будет выброшено исключение и тест не пройдет
    response.cookies[auth_settings.JWT_TOKEN_COOKIE_KEY]
