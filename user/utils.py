def is_support(user):
    return (
        user.is_authenticated
        and (user.is_superuser or user.roles.filter(name="support").exists())
    )