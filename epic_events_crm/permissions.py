from epic_events_crm.authentication import get_current_user


def get_user_permissions_names() -> list[str]:
    """
    Return a list of the current user permissions names.
    Return superuser if the user is from the Superuser department.
    """
    user = get_current_user()
    if user is not None and user.department.name == "Superuser":
        return ["superuser"]
    if user is not None:
        return [permission.name for permission in user.department.permissions]


def requires_permissions(required_permissions: list[str]):
    """
    Decorator to check if the current user has the required permissions.
    superuser is a special permission that allows everything.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            user_permissions = get_user_permissions_names()
            # Check if the user is a superuser
            if "superuser" in user_permissions:
                return func(*args, **kwargs)
            # Check if the user has all the required permissions
            elif all(
                permission in user_permissions for permission in required_permissions
            ):
                return func(*args, **kwargs)
            else:
                print("You don't have the required permissions.")

        return wrapper

    return decorator
