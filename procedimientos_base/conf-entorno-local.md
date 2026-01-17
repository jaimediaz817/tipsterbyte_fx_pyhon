

## COMANDOS API: WEB
- Levanta el servidor local

## COMANDOS PERSONALIZADOS:

- Correr comandos para poblar gestor de ligas:
python manage.py seed-sql LeaguesManagerSeeder
- Correr datos de auth con opción para actualizar de manera forzada cambios en algunos campos:
python manage.py seed-sql AuthSeeder --update