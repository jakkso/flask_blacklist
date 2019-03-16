## Flask_Blacklist

### What
It's a Flask extension designed to work with `sqlalchemy` and `flask_pratorian` to blacklist tokens!

It stores blacklisted JWT's jti value in an in-memory store, allowing blacklist checks without
database calls.  However, when a token is blacklisted, it is also persisted to the database.

### Why

* Emulate a redis store without external dependencies!
    * Almost certainly slower than redis (It's python, after all).
* Why not, it's an excuse to get to know flask a little bit better.

### How
You *are* using a virtualenv, right?

`pip install flask_blacklist` 


Then in your app factory function, initialize `Blacklist` *after* you've initialized your ORM.

    # In global scope
    from flask_blacklist import Blacklist, is_blacklisted
    db = SQLAlchemy()
    guard = Praetorian()
    bl = Blacklist()

    # In the app factory function
    app = Flask(__name__)
    db.init_app(app)
    
    from app.models import Token, User
    bl.init_app(app, Token) # Initialize after your ORM
    
    # is_blacklisted is a helper function that Praetorian uses
    guard.init_app(app, User, is_blacklisted)  
    
The Token database model needs to have two different class methods:
    
* `Token.blacklist_jti` 
    * Takes a single parameter, which is the `jti` string extracted from a JWT
    * Should persist the blacklisted `jti` string to your database.
* `Token.get_blacklisted` 
    * Should return a list of already blacklisted tokens from the database
    * The tokens returns should have a `jti` attribute containing string extracted from the token you want to blacklist

Then, in the route that needs to invalidate the token:

    @auth_blueprint.route("/v1/auth/token", methods=["DELETE"])
    @auth_required
    def invalidate_token():
        token = guard.read_token_from_header()
        jti = guard.extract_jwt_token(token)["jti"]
        bl.blacklist_jti(jti)
        rv, code = {"success": True, "message": "token invalidated"}, 200
        return jsonify(rv), code

<hr>
MIT 
Copyright 2019 Alexander Potts
