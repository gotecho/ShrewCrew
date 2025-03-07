#Tests that flask app is initiated correctly
from app import create_app

def test_app_initialization():
    app = create_app()
    assert app is not None
    assert app.testing is False  # By default, testing mode should be off
