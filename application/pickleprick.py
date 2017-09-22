from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import get_session, setup
from aiohttp import web
import aiohttp_jinja2
import jinja2
from cryptography import fernet
import pickle
import base64


@aiohttp_jinja2.template('pickleprick.html')
async def home(request):
    session = await get_session(request)
    if 'adventures' not in session:
        session['adventures'] = []
    errors = [] if 'errors' not in session else session['errors']
    session['errors'] = []
    return {'adventures': session['adventures'], 'errors': errors}


async def export(request):
    session = await get_session(request)
    if 'adventures' not in session:
        session['adventures'] = []
    prick = pickle.dumps([i for i in session['adventures']])
    pickle_prick = base64.b64encode(prick).decode()
    response = web.Response(text=pickle_prick)
    response.headers['Content-Type'] = 'application/force-download'
    response.headers['Content-Disposition'] = 'attachment; filename=pickle_pRick.data'
    return response


async def do_import(request):
    session = await get_session(request)
    data = await request.post()
    try:
        pickle_prick = data['file'].file.read()
    except:
        session['errors'] = ["Couldn't read pickle prick file."]
        return web.HTTPFound('/')
    prick = base64.b64decode(pickle_prick.decode())
    session['adventures'] = [i for i in pickle.loads(prick)]
    return web.HTTPFound('/')


async def add(request):
    data = await request.post()
    session = await get_session(request)
    if 'adventures' not in session:
        session['adventures'] = []
    errors = []
    for to_check in ("date", "dimension", "planet", "morty"):
        if (to_check not in data) or (len(data[to_check]) < 2):
            errors.append("Error: {} is missing".format(to_check))
    if len(errors) == 0:
        new_adventures = [i for i in session['adventures']]
        new_adventures.append({
            "date": data["date"],
            "dimension": data["dimension"],
            "planet": data["planet"],
            "morty": data["morty"]
        })
        session['adventures'] = new_adventures
    else:
        session['errors'] = errors
    return web.HTTPFound('/')

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./'))
app.router.add_get('/', home)
app.router.add_post('/import', do_import)
app.router.add_get('/export', export)
app.router.add_post('/add', add)
app.router.add_static('/static', "static")
setup(app, EncryptedCookieStorage(base64.urlsafe_b64decode(fernet.Fernet.generate_key())))


def main():
    web.run_app(app)


if __name__ == '__main__':
    main()
