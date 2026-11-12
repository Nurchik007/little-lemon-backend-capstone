LITTLE LEMON - BACK-END DEVELOPER CAPSTONE

A Django REST Framework application with a Django-rendered HTML homepage,
MySQL persistence, a menu API, table bookings, registration and token login.
Codex assisted implementation and testing. This is an educational project.

QUICK START (Python 3.12+, MySQL 8)
1. Create and activate a virtual environment:
   python -m venv .venv
   Windows PowerShell: .\.venv\Scripts\Activate.ps1
   macOS/Linux: source .venv/bin/activate
   python -m pip install -r requirements.txt
   mysqlclient may require the vendor's C client development libraries on Unix.
2. In your own MySQL instance, create a UTF-8 database and a local application
   user. Grant that user privileges only on littlelemon_capstone and
   test_littlelemon_capstone (the latter is for the automated tests).
   Do not use a production database for tests.
3. Export the variables listed in .env.example. That file is only a template;
   settings.py reads the process environment, not an automatically loaded file.
   Generate a key: python -c "import secrets; print(secrets.token_urlsafe(64))"
   PowerShell example: $env:DJANGO_SECRET_KEY = '<your-generated-key>'
   $env:MYSQL_DATABASE = 'littlelemon_capstone'
   $env:MYSQL_TEST_DATABASE = 'test_littlelemon_capstone'
   $env:MYSQL_USER = 'littlelemon'
   $env:MYSQL_PASSWORD = '<your-local-MySQL-password>'
   $env:MYSQL_HOST = '127.0.0.1'
   $env:MYSQL_PORT = '3306'
   $env:DJANGO_DEBUG = '1'
   On Unix, use export NAME=value instead.
4. python manage.py migrate
   python manage.py seed_menu
   python manage.py createsuperuser
   Choose your own local reviewer credentials. They are not supplied or stored
   in this repository. A superuser/staff account can manage the menu.
5. python manage.py runserver 127.0.0.1:8000
   Open http://127.0.0.1:8000/ to view the HTML homepage and static CSS.
6. python manage.py test tests --verbosity 2
   The tests require MySQL and a disposable test database, not SQLite.

API PATHS FOR PEER REVIEW
GET    /                              Django HTML with static CSS
GET    /api/menu/                      Public, paginated menu
POST   /api/menu/                      Staff only
GET    /api/menu/<id>/                 Public item detail
PUT    /api/menu/<id>/                 Staff update
PATCH  /api/menu/<id>/                 Staff partial update
DELETE /api/menu/<id>/                 Staff delete
POST   /api/registration/              username, password; creates normal user
POST   /api/api-token-auth/            username, password -> {"token":"..."}
POST   /api/token/login/               Alias for token login
GET    /api/users/me/                  Current authenticated user
POST   /api/token/logout/              Deletes/revokes the user's token
POST   /auth/users/                    Djoser user registration
POST   /auth/token/login/              Djoser login -> {"auth_token":"..."}
GET    /auth/users/me/                 Djoser current user
POST   /auth/token/logout/             Djoser token revocation
GET    /api/bookings/                  Own bookings; staff can see all
POST   /api/bookings/                  Create booking owned by current user
GET    /api/bookings/<id>/             Own booking or staff
PUT    /api/bookings/<id>/             Update own booking or staff
PATCH  /api/bookings/<id>/             Partial update
DELETE /api/bookings/<id>/             Delete own booking or staff
GET    /admin/                        Django admin; staff login required

COURSE-STYLE COMPATIBILITY PATHS
/restaurant/menu/ and /restaurant/menu/<id>/ map to the same menu views.
/restaurant/booking/tables/ and /restaurant/booking/tables/<id>/ map to
BookingViewSet, registered with DefaultRouter as in the exercise.
/api-token-auth/ also obtains a token.

JSON EXAMPLES
Registration: {"username":"your-local-guest","password":"<your-own-strong-password>"}
Menu: {"title":"Lemon dessert","price":"7.50","inventory":15}
Booking: {"name":"Guest","no_of_guests":2,"booking_date":"2030-11-20T18:00:00Z"}
Use a future date, an explicit timezone, and 1..20 guests.
The owner is assigned by the server. Other users' bookings return 404.
A user cannot reserve the exact same timestamp twice. This demo does not model
individual physical tables, opening hours or restaurant-wide capacity.
Prices are decimal currency values, not floating-point arithmetic.

INSOMNIA
Import insomnia-compatible.postman_collection.json using Import > File.
Insomnia supports Postman v2.1 collections (see the Kong documentation below).
Set base_url to http://127.0.0.1:8000 and supply YOUR OWN local username and
password. Run Register (or create a local staff account), then Token login.
Copy the returned token into the collection's token variable. Requests send
Authorization: Token <token>. Insomnia's Bearer Auth tab is supported too.
Set menu_id and booking_id from newly created records for detail requests.
For menu writes use a staff token; for bookings use a normal guest token.
Expected codes: GET 200; POST 201; PUT/PATCH 200; DELETE 204;
anonymous protected access 401; non-staff menu writes 403; invalid input 400.
The collection contains sample requests, not saved real passwords or tokens.
Local verification used Django's APIClient and an actual HTTP smoke script;
it does not claim that the Insomnia desktop GUI was executed.

DESIGN AND SECURITY
MenuViewSet and BookingViewSet use DRF ModelViewSet for CRUD operations.
BookingViewSet uses ModelViewSet; BookingSerializer and MenuSerializer define
explicit input/output fields. MySQL migrations include positive-price and
guest-count constraints and a unique owner/time index. An atomic save handles
concurrent unique-key conflicts. Django's ORM parameterizes database queries.
The app label capstone_restaurant keeps its tables/migrations separate from
other restaurant examples while retaining the restaurant source package.

Django hashes passwords; registration applies Django password validators and
never accepts staff/superuser permissions. Standard DRF token auth identifies
the user; permission checks restrict writes and filter booking querysets.
Logout revokes the token. The default DRF token does not expire automatically:
use HTTPS and an established expiring-token/OIDC scheme for a real deployment.
Session authentication retains CSRF protection for browser requests.
Anonymous/user throttles and a stricter auth throttle are included; the default
memory-backed throttles are for a single local process, not a DDoS defense.
DEBUG defaults to off and secrets are supplied via environment variables.
The development server and DEBUG=1 setting above are for localhost only.
A production deployment needs a proper web server, HTTPS/cookie settings,
secret management, backups, monitoring, distributed rate limits and a review.
No cloud deployment, production readiness, or remote CI execution is claimed.

UNIT/INTEGRATION TESTS
tests/test_models.py and tests/test_views.py contain the unit/integration tests.
They cover the required model __str__ representation and a serialized
menu-list comparison, plus MySQL persistence, HTML/static links, staff CRUD,
input validation, safe registration, token/Bearer auth, logout revocation,
booking CRUD, cross-user isolation, staff access, duplicate/past bookings,
the compatibility paths, and Djoser registration/login/profile/logout with user-list privacy.
See verification.txt for observed results.

PRIMARY REFERENCES
https://docs.djangoproject.com/en/5.2/ref/databases/#mysql-notes
https://www.django-rest-framework.org/api-guide/authentication/
https://www.django-rest-framework.org/api-guide/permissions/
https://developer.konghq.com/insomnia/import-export/
