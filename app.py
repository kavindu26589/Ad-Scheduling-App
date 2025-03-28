from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from llm_integration import generate_ad_copy, LLM_MODELS
from web_search import perform_web_search
from document_processing import process_schedule_document

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'

db = SQLAlchemy(app)
logging.basicConfig(level=logging.INFO)

class AdCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AdCampaign {self.name}>'

@app.before_first_request
def create_tables():
    db.create_all()
    logging.info("Database tables created.")

@app.route('/')
def index():
    campaigns = AdCampaign.query.order_by(AdCampaign.start_date).all()
    return render_template('index.html', campaigns=campaigns)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        name = request.form['name']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return redirect(url_for('schedule'))
        if end_date < start_date:
            flash('End date cannot be before start date.')
            return redirect(url_for('schedule'))
        # Check for scheduling conflicts.
        conflict = AdCampaign.query.filter(
            AdCampaign.end_date >= start_date,
            AdCampaign.start_date <= end_date
        ).first()
        if conflict:
            flash(f'Conflict with existing campaign: {conflict.name} scheduled from {conflict.start_date} to {conflict.end_date}.')
            return redirect(url_for('schedule'))
        new_campaign = AdCampaign(name=name, start_date=start_date, end_date=end_date)
        db.session.add(new_campaign)
        db.session.commit()
        flash('Ad campaign scheduled successfully.')
        logging.info(f"Scheduled new campaign: {name}")

        # (Optional) Additional analysis can be done here.
        return redirect(url_for('index'))
    return render_template('schedule.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'schedule_file' not in request.files:
            flash("No file part in the request.")
            return redirect(url_for('upload'))
        file = request.files['schedule_file']
        if file.filename == "":
            flash("No file selected.")
            return redirect(url_for('upload'))
        campaigns_data = process_schedule_document(file)
        inserted_campaigns = []
        conflict_campaigns = []
        for campaign in campaigns_data:
            name = campaign.get('name')
            start_date_str = campaign.get('start_date')
            end_date_str = campaign.get('end_date')
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except Exception as e:
                logging.error(f"Error parsing dates for campaign '{name}': {e}")
                conflict_campaigns.append(name)
                continue
            if end_date < start_date:
                conflict_campaigns.append(name)
                continue
            conflict = AdCampaign.query.filter(
                AdCampaign.end_date >= start_date,
                AdCampaign.start_date <= end_date
            ).first()
            if conflict:
                conflict_campaigns.append(name)
                continue
            new_campaign = AdCampaign(name=name, start_date=start_date, end_date=end_date)
            db.session.add(new_campaign)
            inserted_campaigns.append(new_campaign)
        db.session.commit()
        flash(f"Inserted campaigns: {', '.join([c.name for c in inserted_campaigns])}")
        if conflict_campaigns:
            flash(f"Skipped campaigns due to conflicts or errors: {', '.join(conflict_campaigns)}")
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    generated_text = ""
    if request.method == 'POST':
        prompt = request.form['prompt']
        model = request.form.get("model", "llama3.2")
        logging.info("Received prompt for ad copy generation.")
        generated_text = generate_ad_copy(prompt, model)
    return render_template('generate.html', generated_text=generated_text)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Dummy web search endpoint for demonstration.
@app.route('/websearch')
def websearch():
    query = request.args.get('query', 'future programs')
    from web_search import perform_web_search
    results = perform_web_search(query)
    return results

if __name__ == '__main__':
    app.run(debug=True)
