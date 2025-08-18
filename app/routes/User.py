from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.User import User
from services.crud import User as UserService
from typing import List, Dict
import logging
from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.Transaction import Transaction
from models.Balance import Balance

templates = Jinja2Templates(directory="view")
# Configure logging
logger = logging.getLogger(__name__)

user_router = APIRouter()

@user_router.post(
    '/signup',
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user with email and password")
async def signup(data: User, session=Depends(get_session)) -> Dict[str, str]:
    """ Create new user account.
    Args:
        data: User registration data
        session: Database session
    Returns:
        dict: Success message
    Raises:
        HTTPException: If user already exists
    """
    try:
        if UserService.get_user_by_email(data.email, session):
            logger.warning(f"Signup attempt with existing email: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        user = User(
            email=data.email,
            password=data.password)
        UserService.create_user(user, session)
        logger.info(f"New user registered: {data.email}")
        return {"message": "User successfully registered"}

    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@user_router.post('/signin')
async def signin(data: User, session=Depends(get_session)) -> Dict[str, str]:
    """ Authenticate existing user.
    Args:
        form_data: User credentials
        session: Database session
    Returns:
        dict: Success message
    Raises:
        HTTPException: If authentication fails
    """
    user = UserService.get_user_by_email(data.email, session)
    if user is None:
        logger.warning(f"Login attempt with non-existent email: {data.email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    if user.password != data.password:
        logger.warning(f"Failed login attempt for user: {data.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong credentials passed")

    return {"message": "User signed in successfully"}


@user_router.get(
    "/users",
    response_model=List[User],
    summary="Get all users",
    response_description="List of all users"
)
async def get_all_users(session=Depends(get_session)) -> List[User]:
    try:
        users = UserService.get_all_users(session)
        logger.info(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )

@user_router.get("/signup", tags=["user"])
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# --- ОБРАБОТЧИК ФОРМЫ (POST из <form>) ---

@user_router.post("/signup", tags=["user"])  # тот же путь, но другой метод
async def signup_from_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session=Depends(get_session),
):
    # Минимальная валидация
    errors = []
    if "@" not in email or "." not in email:
        errors.append("Некорректный e-mail")
    if not password:
        errors.append("Пароль обязателен")
    if errors:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "errors": errors, "email": email},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Проверка существования и создание (тем же сервисом)
    if UserService.get_user_by_email(email, session):
        return templates.TemplateResponse(
            "signup.html", {"request": request, "errors": ["Пользователь уже существует"], "email": email},
            status_code=status.HTTP_409_CONFLICT
        )

    user = User(email=email, password=password)
    UserService.create_user(user, session)

    # После регистрации отправим на страницу входа
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@user_router.get("/{user_id}/balance")
async def get_user_balance(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    # 1) Берём текущее число из БД (сумма всех движений по пользователю)
    result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(Transaction.user_id == user_id)
    )
    amount = float(result.scalar_one())

    # 2) Оборачиваем в твой класс и возвращаем через его API
    bal = Balance(amount)
    return {"user_id": user_id, "balance": bal.get_balance()}