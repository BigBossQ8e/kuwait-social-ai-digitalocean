"""
Reporting and Analytics Models for Kuwait Social AI
"""

from datetime import datetime
from sqlalchemy import func
from . import db


class ReportTemplate(db.Model):
    """Customizable report templates"""
    __tablename__ = 'report_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    
    # Template details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(50))  # performance, competitor, roi, engagement
    
    # Configuration
    sections = db.Column(db.JSON)  # List of sections to include
    metrics = db.Column(db.JSON)  # Specific metrics to track
    comparison_period = db.Column(db.String(20))  # previous_period, year_over_year
    
    # Branding
    include_logo = db.Column(db.Boolean, default=True)
    brand_colors = db.Column(db.JSON)
    custom_header = db.Column(db.Text)
    custom_footer = db.Column(db.Text)
    
    # Scheduling
    is_scheduled = db.Column(db.Boolean, default=False)
    schedule_frequency = db.Column(db.String(20))  # daily, weekly, monthly
    schedule_day = db.Column(db.Integer)  # Day of week/month
    schedule_time = db.Column(db.Time)
    
    # Distribution
    email_recipients = db.Column(db.JSON)
    auto_send = db.Column(db.Boolean, default=False)
    
    # Metadata
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='report_templates')
    generated_reports = db.relationship('GeneratedReport', back_populates='template', lazy='dynamic')
    
    def __repr__(self):
        return f'<ReportTemplate {self.name}>'


class GeneratedReport(db.Model):
    """Generated PDF reports"""
    __tablename__ = 'generated_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'))
    
    # Report details
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50))
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # File information
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)  # In bytes
    page_count = db.Column(db.Integer)
    
    # Content summary
    key_metrics = db.Column(db.JSON)
    insights = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    
    # Performance comparison
    performance_change = db.Column(db.JSON)  # Metrics compared to previous period
    
    # Generation details
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    generation_time_seconds = db.Column(db.Float)
    
    # Access tracking
    download_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    shared_with = db.Column(db.JSON)  # Email addresses
    
    # Relationships
    client = db.relationship('Client', back_populates='generated_reports')
    template = db.relationship('ReportTemplate', back_populates='generated_reports')
    
    def __repr__(self):
        return f'<GeneratedReport {self.title}>'


class ROITracking(db.Model):
    """Track ROI for social media campaigns"""
    __tablename__ = 'roi_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Campaign details
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    campaign_name = db.Column(db.String(100))
    
    # Time period
    tracking_date = db.Column(db.Date, nullable=False)
    
    # Investment
    content_creation_cost = db.Column(db.Float, default=0.0)
    advertising_spend = db.Column(db.Float, default=0.0)
    influencer_cost = db.Column(db.Float, default=0.0)
    tool_cost = db.Column(db.Float, default=0.0)  # Platform subscription
    total_investment = db.Column(db.Float, default=0.0)
    
    # Returns - Direct
    direct_sales_revenue = db.Column(db.Float, default=0.0)
    promo_code_revenue = db.Column(db.Float, default=0.0)
    attributed_transactions = db.Column(db.Integer, default=0)
    average_order_value = db.Column(db.Float, default=0.0)
    
    # Returns - Indirect
    new_customers_acquired = db.Column(db.Integer, default=0)
    customer_lifetime_value = db.Column(db.Float, default=0.0)
    brand_mention_value = db.Column(db.Float, default=0.0)
    earned_media_value = db.Column(db.Float, default=0.0)
    
    # Social metrics
    total_reach = db.Column(db.Integer, default=0)
    total_engagement = db.Column(db.Integer, default=0)
    website_traffic_from_social = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Float, default=0.0)
    
    # Calculated ROI
    roi_percentage = db.Column(db.Float, default=0.0)
    payback_period_days = db.Column(db.Integer)
    
    # Attribution
    attribution_model = db.Column(db.String(50))  # first_touch, last_touch, multi_touch
    confidence_score = db.Column(db.Float)  # 0-100
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='roi_tracking')
    campaign = db.relationship('Campaign', back_populates='roi_tracking')
    
    def calculate_roi(self):
        """Calculate ROI percentage"""
        if self.total_investment > 0:
            total_returns = (
                self.direct_sales_revenue + 
                self.promo_code_revenue + 
                self.earned_media_value +
                (self.new_customers_acquired * self.customer_lifetime_value)
            )
            self.roi_percentage = ((total_returns - self.total_investment) / self.total_investment) * 100
        else:
            self.roi_percentage = 0
        
        return self.roi_percentage
    
    def __repr__(self):
        return f'<ROITracking {self.campaign_name} - {self.tracking_date}>'


class AnalyticsDashboard(db.Model):
    """Custom analytics dashboard configurations"""
    __tablename__ = 'analytics_dashboards'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Dashboard details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    
    # Layout configuration
    layout = db.Column(db.JSON)  # Grid layout configuration
    widgets = db.Column(db.JSON)  # List of widgets and their configs
    
    # Data settings
    default_date_range = db.Column(db.String(20))  # last_7_days, last_30_days, etc.
    refresh_interval_minutes = db.Column(db.Integer, default=60)
    
    # Sharing
    is_public = db.Column(db.Boolean, default=False)
    shared_with = db.Column(db.JSON)  # User IDs
    public_url = db.Column(db.String(100), unique=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='analytics_dashboards')
    
    def __repr__(self):
        return f'<AnalyticsDashboard {self.name}>'


class MetricAlert(db.Model):
    """Alerts for metric thresholds"""
    __tablename__ = 'metric_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Alert configuration
    name = db.Column(db.String(100), nullable=False)
    metric_name = db.Column(db.String(50))  # engagement_rate, follower_count, etc.
    condition = db.Column(db.String(20))  # greater_than, less_than, equals
    threshold_value = db.Column(db.Float)
    
    # Alert settings
    check_frequency = db.Column(db.String(20))  # hourly, daily, weekly
    alert_channels = db.Column(db.JSON)  # email, sms, in_app
    recipients = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_triggered = db.Column(db.DateTime)
    trigger_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='metric_alerts')
    
    def __repr__(self):
        return f'<MetricAlert {self.name}>'


class BenchmarkData(db.Model):
    """Industry benchmark data for Kuwait"""
    __tablename__ = 'benchmark_data'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Benchmark details
    industry = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    metric_name = db.Column(db.String(50), nullable=False)
    
    # Values
    average_value = db.Column(db.Float)
    median_value = db.Column(db.Float)
    top_10_percent = db.Column(db.Float)
    top_25_percent = db.Column(db.Float)
    bottom_25_percent = db.Column(db.Float)
    
    # Context
    sample_size = db.Column(db.Integer)
    data_period = db.Column(db.String(20))  # Q1_2024, etc.
    account_size_range = db.Column(db.String(50))  # 1k-10k, 10k-100k, etc.
    
    # Metadata
    source = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BenchmarkData {self.industry} - {self.metric_name}>'