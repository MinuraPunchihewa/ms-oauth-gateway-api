from flask import request, redirect, session, render_template
import msal
import requests

from utils.ms_delegated_permissions_manager import MSDelegatedPermissionsManager


# Initialize the token cache.
cache = msal.SerializableTokenCache()

# Load the cache from file if it exists.
cache_file = 'cache.bin'
try:
    cache_content = open(cache_file, 'r').read()
except FileNotFoundError:
    cache_content = None

if cache_content:
    cache.deserialize(cache_content)


def register_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            client_id = request.form.get('client_id')
            client_secret = request.form.get('client_secret')
            tenant_id = request.form.get('tenant_id')

            # Save the client ID, client secret, and tenant ID in the session.
            session['client_id'] = client_id
            session['client_secret'] = client_secret
            session['tenant_id'] = tenant_id

            perms_manager = MSDelegatedPermissionsManager(
                client_id=client_id,
                client_secret=client_secret,
                tenant_id=tenant_id,
                cache=cache,
            )

            auth_url = perms_manager.get_auth_url()

            return redirect(auth_url)
    

    @app.route('/callback', methods=['GET'])
    def callback():
        code = request.args.get('code')

        perms_manager = MSDelegatedPermissionsManager(
            client_id=session.get('client_id'),
            client_secret=session.get('client_secret'),
            tenant_id=session.get('tenant_id'),
            cache=cache,
            code=code,
        )

        access_token = perms_manager.get_access_token()

        return redirect(f'/profile?access_token={access_token}')
    

    @app.route('/profile', methods=['GET'])
    def profile():
        access_token = request.args.get('access_token')

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)

        return response.json()
