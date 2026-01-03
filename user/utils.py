from .models import Role
def is_support(user):
    return user.is_authenticated and (
        user.is_superuser or user.roles.filter(name=Role.Names.SUPPORT).exists()
    )

def is_performer(user):
    print("Checking if user is performer..." +  str(user.roles.filter(name=Role.Names.PERFORMER).exists()))
    print("name " + str(Role.Names.PERFORMER))
    return user.is_authenticated and (
        user.is_superuser or user.roles.filter(name=Role.Names.PERFORMER).exists()
    )



