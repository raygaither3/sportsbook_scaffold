from datetime import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from .extensions import login_manager, db, migrate, bcrypt, csrf
from .models import create_database
from .auth.routes import auth 
from .main.routes import main 
from .user.routes import user
from .bets.routes import bets
from .admin.routes import admin




def create_app(config_class='config.DevelopmentConfig'):
    app = Flask(__name__)
    Bootstrap5(app)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(bets, url_prefix='/bets')
    app.register_blueprint(admin, url_prefix='/admin')

    # Create database
    create_database(app)

     # Register custom Jinja filters
    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        try:
            return datetime.fromisoformat(value).strftime('%b %d, %Y – %I:%M %p')
        except Exception:
            return value  
        
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow}
    
 

    return app
