from typing import List, Text

import msal


class MSDelegatedPermissionsManager:
    """
    The class for managing the delegated permissions for the Microsoft Graph API.
    """
    def __init__(
        self,
        client_id: Text,
        client_secret: Text,
        tenant_id: Text,
        cache: msal.SerializableTokenCache,
        scopes: List = ["https://graph.microsoft.com/.default"],
        code: Text = None,
    ) -> None:
        """
        Initializes the delegated permissions manager.

        Args:
            client_id (Text): The client ID of the application registered in Microsoft Entra ID.
            client_secret (Text): The client secret of the application registered in Microsoft Entra ID.
            tenant_id (Text): The tenant ID of the application registered in Microsoft Entra ID.
            cache (msal.SerializableTokenCache): The token cache for storing the access token.
            scopes (List): The scopes for the Microsoft Graph API.
            code (Text): The authentication code for acquiring the access token.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.cache = cache
        self.scopes = scopes
        self.code = code

    def get_auth_url(self) -> Text:
        """
        Returns the authorization request URL for the Microsoft Graph API.

        Returns:
            Text: The authorization request URL for the Microsoft Graph API.
        """
        msal_app = self._get_msal_app()

        auth_url = msal_app.get_authorization_request_url(
            scopes=self.scopes
        )

        return auth_url

    def get_access_token(self) -> Text:
        """
        Retrieves an access token for the Microsoft Graph API.
        If a valid access token is found in the cache, it is returned.
        Otherwise, the authentication flow is executed.

        Returns:
            Text: The access token for the Microsoft Graph API.
        """
        # Check if a valid access token is already in the cache for the signed-in user.
        msal_app = self._get_msal_app()
        accounts = msal_app.get_accounts()

        if accounts:
            response = msal_app.acquire_token_silent(self.scopes, account=accounts[0])
            if "access_token" in response:
                return response['access_token']

        # If no valid access token is found in the cache, run the authentication flow.
        response = msal_app.acquire_token_by_authorization_code(
            code=self.code,
            scopes=self.scopes
        )

        if "access_token" in response:
            return response['access_token']

    def _get_msal_app(self) -> msal.ConfidentialClientApplication:
        """
        Returns an instance of the MSAL ConfidentialClientApplication.

        Returns:
            msal.ConfidentialClientApplication: An instance of the MSAL ConfidentialClientApplication.
        """
        return msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
            token_cache=self.cache,
        )

