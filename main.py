import asyncio
from sanic import Sanic
from sanic.response import text, redirect
from sanic.response import json as json_resp
from data import store
from polls.poll import Poll
from twitch import Twitch
from twitch.verify import verify_header
import template
import datetime
import json

t = Twitch()

p = None

app = Sanic("TwitchOligarchy Overlay")


@app.get('/start_login')
async def start_login(request):
    url = t.get_user_redirect_url()
    return redirect(url)


@app.route("/callback", methods=['GET', 'POST'])
async def callback(request):
    if not(verify_header(request.headers['twitch-eventsub-message-signature'], request.headers['twitch-eventsub-message-id'], request.headers['twitch-eventsub-message-timestamp'], request.body)):
        return text("sig not ok", status=403)
    print("handling request with OK sig.")
    if request.json.get('challenge'):
        print("found challenge - responding")
        return text(request.json.get('challenge'), status=200)
    t.handle(request.json)
    return text("received.")


@app.get('/callback_user')
async def callback_user(request):
    if request.args.get('code') is None:
        return text('need code', status=405)
    r = t.get_user_access_token(request.args.get('code'))
    app.add_task(t.register_eventsub())
    return redirect(app.url_for('index'))


@app.get('/')
async def index(request):
    user = t.get_user()
    auth = t.refresh_user_access_token()
    if user.get('data', [{}])[0].get('id') is None:
        return redirect(app.url_for('start_login'))
    if auth is None:
        return redirect(app.url_for('start_login'))
    try:
        return template.render("index.j2.html", name="hello!")
    except FileNotFoundError:
        return text("404, file not found.", status=404)


@app.get('/static/<filename:path>')
async def static(request, filename):
    try:
        return await template.static(filename)
    except FileNotFoundError:
        return text("404, file not found.", status=404)


@app.get('/api/token')
async def token(request):
    return json_resp(t.refresh_user_access_token())


@app.get('/api/user')
async def user(request):
    return json_resp(t.get_user().get('data', [{}])[0])


@app.get('/api/poll')
async def poll(request):
    p = t.get_poll()
    if p is None:
        return json_resp({'message': 'no active poll'})
    return json_resp(p.__dict__())
if __name__ == '__main__':
    app.add_task(t.register_eventsub())
    app.run(host='0.0.0.0', port=8443, debug=True)
