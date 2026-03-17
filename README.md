# Teappot: Módulo Authentication (Auth) 

Módulo para control de accesos de usuarios.

**Requisitos**

Django Apps: teacore

## Variables de entorno

**AUTH_BACKOFFICE** *(True|False)*: Permite el acceso a la página de su propia cuenta.

**AUTH_SELF_CREATE** *(True|False)*: Permite la creación de la cuenta por autoatención.

**AUTH_SELF_RECOVERY** *(True|False)*: Permite la recuperación de la cuenta por autoatención.

**AUTH_EMAIL_AS_USERNAME** *(True)*: Utiliza el correo como nomnbre de usuario. (Aún no está listo ni probado utilizar el nombre de usuario solo)

**AUTH_DEFAULT_REDIRECT** *(url|app:view)*: Ruta para la redirección en login exitoso.

**AUTH_DEFAULT_HOME** *(url|app:view)*: Redirección en login exitoso

**AUTH_AUTO_ACTIVATE** *(True|False)*: El usuario queda activado al crear su cuenta (True) o no se activa auto al crear mandando un correo para crear su password y activar su cuenta.

**AUTH_TASK_TOKEN_LIFETIME** *(minutos:int)*: Duración del token de la sesión del API en minutos.

## Consideraciones generales

- Al recuperar la cuenta **nunca hay que activar la cuenta** ya que su uso está reservado para ni eliminar el usuario.