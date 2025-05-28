from flask import Blueprint, request, jsonify, redirect, url_for, abort, send_file, current_app
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from python_conversion.models import Campaign, CampaignList, CampaignCriterion, CampaignListFieldset, CampaignListFieldsetField
from python_conversion.forms import CampaignForm, CampaignCriterionForm, CampaignListForm, SubqueryDialogForm
from python_conversion.extensions import db

campaign_bp = Blueprint('campaign', __name__, url_prefix='/campaign')

@campaign_bp.route('/index')
def index():
    show_counts = request.args.get('show_counts', 'false').lower() == 'true'
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

    if include_deleted:
        campaigns = Campaign.query.all()
    else:
        campaigns = Campaign.query.filter(Campaign.deleted_at == None).all()

    # For simplicity, returning JSON list of campaigns
    return jsonify({
        'show_counts': show_counts,
        'include_deleted': include_deleted,
        'campaigns': [c.to_dict() for c in campaigns]
    })

@campaign_bp.route('/show/<int:id>')
def show(id):
    campaign = Campaign.query.get_or_404(id)
    exclude = request.args.get('exclude', '')
    excludes = exclude.split(',') if exclude else []
    household = request.args.get('household', 'false').lower() == 'true'

    if household:
        counts = campaign.get_household_counts(excludes)
        universe = campaign.get_household_universe(excludes)
        states = campaign.get_household_counts_by_state(excludes)
    else:
        counts = campaign.get_counts(excludes)
        universe = campaign.get_universe(excludes)
        states = campaign.get_counts_by_state(excludes)

    return jsonify({
        'counts': counts,
        'universe': universe,
        'states': states
    })

@campaign_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    campaign = Campaign.query.get(id)
    if not campaign:
        campaign = Campaign()
    form = CampaignForm(obj=campaign)

    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(campaign)
            db.session.add(campaign)
            db.session.commit()
            return redirect(url_for('campaign.index'))
    # For GET or failed POST, return form data as JSON (simplified)
    return jsonify({
        'campaign': campaign.to_dict(),
        'form_errors': form.errors
    })

@campaign_bp.route('/new')
def new():
    return redirect(url_for('campaign.edit', id=0))

@campaign_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    campaign = Campaign.query.get_or_404(id)
    campaign.deleted_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('campaign.index'))

@campaign_bp.route('/undelete/<int:id>', methods=['POST'])
def undelete(id):
    campaign = Campaign.query.get_or_404(id)
    campaign.deleted_at = None
    db.session.commit()
    return redirect(url_for('campaign.index'))

@campaign_bp.route('/copy/<int:id>', methods=['POST'])
def copy(id):
    campaign = Campaign.query.get_or_404(id)
    copy_campaign = campaign.copy()  # Implement copy method in model
    db.session.add(copy_campaign)
    db.session.commit()
    return redirect(url_for('campaign.edit', id=copy_campaign.id))

@campaign_bp.route('/pulls')
def pulls():
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    lists = CampaignList.query.filter(CampaignList.created_at >= one_year_ago).all()
    return jsonify([l.to_dict() for l in lists])

@campaign_bp.route('/request/<int:id>', methods=['GET', 'POST'])
def request_list(id):
    campaign = Campaign.query.get_or_404(id)
    list_obj = CampaignList()
    list_obj.campaign = campaign
    form = CampaignListForm(obj=list_obj)

    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(list_obj)
            db.session.add(list_obj)
            db.session.commit()
            return redirect(url_for('campaign.pulls'))
    return jsonify({
        'form_errors': form.errors
    })

@campaign_bp.route('/download/<int:id>')
def download(id):
    list_obj = CampaignList.query.get_or_404(id)
    file_path = current_app.config['ROOT_DIR'] + '/lists/' + list_obj.get_file_name() + '.zip'
    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# Additional AJAX routes and helper functions would be implemented similarly.
