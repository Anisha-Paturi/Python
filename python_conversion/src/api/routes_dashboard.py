from flask import Blueprint, jsonify
from login_backend_python.extensions import db
from python_conversion.token_filter import token_required
from python_conversion.models import get_dashboard_index_stats, get_dashboard_newdemos_states, get_dashboard_responder_file_data
from python_conversion.feedmanager_report import FeedManagerReport

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/index', methods=['GET'])
@token_required(dashboard_bp)
def dashboard_index(current_user):
    resp = {}
    top10 = get_dashboard_index_stats(db)
    resp["stats"] = top10
    return jsonify(resp)

@dashboard_bp.route('/mailed', methods=['GET'])
@token_required(dashboard_bp)
def dashboard_mailed(current_user):
    # Empty method in PHP, returning empty JSON
    return jsonify({})

@dashboard_bp.route('/policy2009', methods=['GET'])
@token_required(dashboard_bp)
def dashboard_policy2009(current_user):
    # Empty method in PHP, returning empty JSON
    return jsonify({})

@dashboard_bp.route('/potential', methods=['GET'])
@token_required(dashboard_bp)
def dashboard_potential(current_user):
    # Empty method in PHP, returning empty JSON
    return jsonify({})

@dashboard_bp.route('/responserate', methods=['GET'])
@token_required(dashboard_bp)
def dashboard_responserate(current_user):
    # Empty method in PHP, returning empty JSON
    return jsonify({})

@dashboard_bp.route('/newdemos', methods=['GET'])
@token_required(dashboard_bp)
def dashboard_newdemos(current_user):
    states = get_dashboard_newdemos_states(db)
    return jsonify(states)

@dashboard_bp.route('/responderFile', methods=['GET'])
@token_required(dashboard_bp)
def dashboard_responderFile(current_user):
    data = get_dashboard_responder_file_data(db)
    return jsonify(data)

@dashboard_bp.route('/feedmanagerreport', methods=['GET'])
@token_required(dashboard_bp)
def feed_manager_report(current_user):
    # Example usage of FeedManagerReport class
    report = FeedManagerReport.factory()
    results = report.execute(db.session)
    # Convert results to list of dicts
    data = [dict(row) for row in results]
    return jsonify(data)
