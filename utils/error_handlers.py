"""
Centralized Error Handlers for RentVerify
"""
from flask import jsonify, render_template

class RentVerifyException(Exception):
    """Custom exception for RentVerify business logic."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        if app.config.get('RETURN_JSON_ERRORS', False):
            return jsonify({"error": "Bad Request", "message": str(error)}), 400
        return render_template('error.html', code=400, message="Bad Request"), 400

    @app.errorhandler(404)
    def not_found(error):
        if app.config.get('RETURN_JSON_ERRORS', False):
            return jsonify({"error": "Not Found", "message": str(error)}), 404
        return render_template('error.html', code=404, message="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        if app.config.get('RETURN_JSON_ERRORS', False):
            return jsonify({"error": "Internal Server Error", "message": str(error)}), 500
        return render_template('error.html', code=500, message="Internal Server Error"), 500

    @app.errorhandler(RentVerifyException)
    def handle_rentverify_exception(error):
        if app.config.get('RETURN_JSON_ERRORS', False):
            return jsonify({"error": "Custom Error", "message": error.message}), error.status_code
        return render_template('error.html', code=error.status_code, message=error.message), error.status_code
