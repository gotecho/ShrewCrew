from flask import Flask

try: 
    from request_flow.routes.sms_routes import sms_bp
    print("sms_routes loaded")
except Exception as e:
    print(f"Error loading sms_routes: {e}")

try:
    from request_flow.routes.webhook_routes import webhook_bp
    print("webhook_routes loaded")
except Exception as e:
    print(f"Error loading webhook_routes: {e}")

try:
    from request_flow.routes.overview import overview_bp
    print("overview loaded")
except Exception as e:
    print(f"Error loading overview: {e}")

try:
    from request_flow.routes.test_routes import test_bp
    print("test_routes loaded")
except Exception as e:
    print(f"Error loading test_routes: {e}")

def create_app():
    app = Flask(__name__)

    try:    
        # Register blueprints
        app.register_blueprint(sms_bp)
        app.register_blueprint(webhook_bp)
        app.register_blueprint(overview_bp)
        app.register_blueprint(test_bp)
        print("All blueprints registered")
    except Exception as e:
        print(f"Error registering blueprints: {e}")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)