import os
import pickle

from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.urls import reverse
from google_auth_oauthlib.flow import Flow as GoogleFlow
from googleapiclient.discovery import build as GoogleApiClientBuild
from youtube_auth.models import YoutubeCredential
from youtube_vault.tasks import import_youtube_playlists

CLIENT_SECRETS_FILE = os.path.join(os.getcwd(), "client_secret.json")
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


FLOW = GoogleFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

def oauth2callback(request):
    FLOW.redirect_uri = request.build_absolute_uri(reverse("oauth2callback"))
    authorization_response = request.get_full_path()
    FLOW.fetch_token(authorization_response=authorization_response)
    oauth_service = GoogleApiClientBuild("oauth2", "v2", credentials=FLOW.credentials)
    email = oauth_service.userinfo().get().execute().get("email")
    first_name = oauth_service.userinfo().get().execute().get("given_name", "")
    last_name = oauth_service.userinfo().get().execute().get("family_name", "")
    user, _ = get_user_model().objects.get_or_create(
        username=email,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,
        is_superuser=True,
        email=email,
    )
    user.set_unusable_password()
    youtube_credential_obj, created = YoutubeCredential.objects.get_or_create(
        client_id=FLOW.credentials.client_id,
        user=user
    )
    youtube_credential_obj._credentials = pickle.dumps(FLOW.credentials)
    youtube_credential_obj.save()
    user.credentials.add(youtube_credential_obj)
    user.save()
    login(request, user)
    if created:
        import_youtube_playlists(youtube_credential_obj.id)
    return redirect("admin:index")


def auth(request):
    FLOW.redirect_uri = request.build_absolute_uri(reverse("oauth2callback"))
    authorization_url, state = FLOW.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        approval_prompt="force",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )
    return redirect(authorization_url)
