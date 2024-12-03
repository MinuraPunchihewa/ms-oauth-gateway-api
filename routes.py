from flask import request, redirect
import msal

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
    @app.route('/login', methods=['POST'])
    def login():
        data = request.json

        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        tenant_id = data.get('tenant_id')

        perms_manager = MSDelegatedPermissionsManager(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            cache=cache,
        )

        auth_url = perms_manager.get_auth_url()

        return redirect(auth_url)