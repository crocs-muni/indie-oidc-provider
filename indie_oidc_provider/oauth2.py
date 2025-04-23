from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.integrations.flask_oauth2 import (
    AuthorizationServer as _AuthorizationServer,
)
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_bearer_token_validator,
)
from authlib.oauth2.rfc6749.grants import (
    AuthorizationCodeGrant as _AuthorizationCodeGrant,
)
from authlib.oidc.core.grants import (
    OpenIDCode as _OpenIDCode,
    OpenIDImplicitGrant as _OpenIDImplicitGrant,
    OpenIDHybridGrant as _OpenIDHybridGrant,
)
from authlib.oidc.core import UserInfo
from werkzeug.security import gen_salt
from .models import db, User
from .models import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token

from flask import current_app


# DUMMY_JWT_CONFIG = {
#     "key": "secret",
#     "alg": "HS256",
#     "iss": "https://authlib.org",
#     "exp": 3600,
# }
# DUMMY_JWT_CONFIG = {
#     "crv": "P-256",
#     "d": "p9Bbmkr0mrqE3HuYqR4hdblH85BO3jiaKI3DQo_YjeY",
#     "kid": "exapmle",
#     "kty": "EC",
#     "x": "Kp9RBOl7QILm9KSbgSaCQbj1OSFLFE7Euvk3hnDlTqo",
#     "y": "TOH8T09IfxObId_g0IlKOPXU-9jiDPylXV5iKsNSedI",
# }


def exists_nonce(nonce, req):
    exists = OAuth2AuthorizationCode.query.filter_by(
        client_id=req.client_id, nonce=nonce
    ).first()
    return bool(exists)


def generate_user_info(user, scope):
    return UserInfo(sub=str(user.id), name=user.username)


def create_authorization_code(client, grant_user, request):
    code = gen_salt(48)
    nonce = request.data.get("nonce")
    item = OAuth2AuthorizationCode(
        code=code,
        client_id=client.client_id,
        redirect_uri=request.redirect_uri,
        scope=request.scope,
        user_id=grant_user.id,
        nonce=nonce,
    )
    db.session.add(item)
    db.session.commit()
    return code


class AuthorizationCodeGrant(_AuthorizationCodeGrant):
    # def create_authorization_code(self, client, grant_user, request):
    #     code = create_authorization_code(client, grant_user, request)
    #     print(f"Code: {code} created")
    #     return code

    def parse_authorization_code(self, code, client):
        item = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id
        ).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)

    def query_authorization_code(self, code, client):
        exists = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id
        ).first()
        if exists:
            return exists

    def save_authorization_code(self, code, request):
        nonce = request.data.get("nonce")
        client = request.client
        user = request.user

        item = OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=user.id,
            nonce=nonce,
        )
        db.session.add(item)
        db.session.commit()
        return item


class OpenIDCode(_OpenIDCode):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_audiences(self, request):
        return ["zkLogin"]

    def get_jwt_config(self, grant):
        key = current_app.config["OAUTH2_JWT_KEY"]
        alg = current_app.config["OAUTH2_JWT_ALG"]
        iss = current_app.config["OAUTH2_JWT_ISS"]
        return dict(key=key, alg=alg, iss=iss, exp=3600)

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


class ImplicitGrant(_OpenIDImplicitGrant):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_audiences(self, request):
        return ["zkLogin"]

    def get_jwt_config(self, grant):
        key = current_app.config["OAUTH2_JWT_KEY"]
        alg = current_app.config["OAUTH2_JWT_ALG"]
        iss = current_app.config["OAUTH2_JWT_ISS"]
        return dict(key=key, alg=alg, iss=iss, exp=3600)

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


class HybridGrant(_OpenIDHybridGrant):
    def create_authorization_code(self, client, grant_user, request):
        return create_authorization_code(client, grant_user, request)

    def get_audiences(self, request):
        return ["zkLogin"]

    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self, grant):
        key = current_app.config["OAUTH2_JWT_KEY"]
        alg = current_app.config["OAUTH2_JWT_ALG"]
        iss = current_app.config["OAUTH2_JWT_ISS"]
        return dict(key=key, alg=alg, iss=iss, exp=3600)

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


# class AuthorizationServer(_AuthorizationServer):
#     def save_authorization_code(self, code, request):
#         client = request.client
#         item = OAuth2AuthorizationCode(
#             code=code,
#             client_id=client.client_id,
#             redirect_uri=request.redirect_uri,
#             scope=request.scope,
#             user_id=request.user.id,
#         )
#         item.save()


authorization = _AuthorizationServer()
require_oauth = ResourceProtector()


def config_oauth(app):
    query_client = create_query_client_func(db.session, OAuth2Client)
    save_token = create_save_token_func(db.session, OAuth2Token)
    authorization.init_app(app, query_client=query_client, save_token=save_token)

    # support all openid grants
    authorization.register_grant(
        AuthorizationCodeGrant,
        [
            OpenIDCode(require_nonce=True),
        ],
    )
    authorization.register_grant(ImplicitGrant)
    authorization.register_grant(HybridGrant)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
