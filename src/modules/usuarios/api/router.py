"""
Router de FastAPI para el módulo de Usuarios.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.modules.usuarios.application.features.register_user.use_case import RegisterUserUseCase, RegisterUserCommand
from src.modules.usuarios.application.features.login.use_case import LoginUseCase, LoginResponse
from src.modules.usuarios.api.dependencies import get_register_use_case, get_login_use_case, get_current_user
from src.modules.usuarios.domain.entities import User
from src.core.exceptions import BusinessRuleViolation

router = APIRouter()

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario"
)
async def register(
    command: RegisterUserCommand,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)]
):
    try:
        user = await use_case.execute(command)
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "message": "Usuario registrado exitosamente"
        }
    except BusinessRuleViolation as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Iniciar sesión y obtener token JWT"
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[LoginUseCase, Depends(get_login_use_case)]
):
    try:
        return await use_case.execute(form_data.username, form_data.password)
    except BusinessRuleViolation as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get(
    "/me",
    summary="Obtener perfil del usuario actual"
)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "user_id": str(current_user.user_id),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    }
