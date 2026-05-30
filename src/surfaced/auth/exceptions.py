from fastapi import HTTPException, status

InvalidCredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
)

TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
)

EmailExistsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
)

UserNotFoundException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
)

InactiveUserException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="User is not active"
)

TokenInvalidException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
)

RateLimitExceededException = HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Too many attempts. Please try again later",
)
