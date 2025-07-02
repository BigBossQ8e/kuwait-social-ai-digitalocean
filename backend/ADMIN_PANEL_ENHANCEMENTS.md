# 🚀 Admin Panel Feature Enhancements & Technical Hardening

> **Created**: July 2, 2025  
> **Purpose**: Enhanced features for proactive monitoring, security, and UX improvements

---

## 1. 💰 Cost & Usage Anomaly Detection System

### Overview
Move from passive monitoring to **proactive cost management** with automated alerts and predictive analytics.

### Implementation Details

#### 1.1 Database Schema
```sql
-- Anomaly Detection Rules
CREATE TABLE anomaly_rules (
    id SERIAL PRIMARY KEY,
    rule_type VARCHAR(50) NOT NULL, -- 'usage_spike', 'budget_projection', 'pattern_deviation'
    service_name VARCHAR(100),
    threshold_value DECIMAL(10,2),
    threshold_type VARCHAR(50), -- 'percentage', 'absolute', 'rate'
    time_window INTEGER, -- in minutes
    severity VARCHAR(20), -- 'warning', 'critical'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomaly Alerts
CREATE TABLE anomaly_alerts (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES anomaly_rules(id),
    client_id INTEGER REFERENCES clients(id),
    service_name VARCHAR(100),
    alert_type VARCHAR(50),
    current_value DECIMAL(10,2),
    expected_value DECIMAL(10,2),
    deviation_percentage DECIMAL(5,2),
    message TEXT,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_by INTEGER REFERENCES admins(id),
    acknowledged_at TIMESTAMP
);

-- Usage Patterns (for ML-based detection)
CREATE TABLE usage_patterns (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    service_name VARCHAR(100),
    hour_of_day INTEGER,
    day_of_week INTEGER,
    average_usage DECIMAL(10,2),
    std_deviation DECIMAL(10,2),
    sample_count INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 1.2 Anomaly Detection Service
```python
# services/anomaly_detection_service.py
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func
from models import db, Client, APIUsage, AnomalyRule, AnomalyAlert, UsagePattern

class AnomalyDetectionService:
    def __init__(self):
        self.alert_cooldown = 30  # minutes between alerts for same issue
        
    def check_usage_anomalies(self):
        """Main method to check all anomaly rules"""
        active_rules = AnomalyRule.query.filter_by(is_active=True).all()
        
        for rule in active_rules:
            if rule.rule_type == 'usage_spike':
                self._check_usage_spikes(rule)
            elif rule.rule_type == 'budget_projection':
                self._check_budget_projections(rule)
            elif rule.rule_type == 'pattern_deviation':
                self._check_pattern_deviations(rule)
    
    def _check_usage_spikes(self, rule: AnomalyRule):
        """Detect sudden spikes in usage"""
        time_window = datetime.utcnow() - timedelta(minutes=rule.time_window)
        
        # Get recent usage by client
        usage_data = db.session.query(
            APIUsage.client_id,
            func.sum(APIUsage.tokens_used).label('total_usage')
        ).filter(
            APIUsage.timestamp >= time_window,
            APIUsage.service_name == rule.service_name
        ).group_by(APIUsage.client_id).all()
        
        for client_id, current_usage in usage_data:
            # Get historical average for comparison
            historical_avg = self._get_historical_average(
                client_id, 
                rule.service_name, 
                rule.time_window
            )
            
            if historical_avg > 0:
                spike_percentage = ((current_usage - historical_avg) / historical_avg) * 100
                
                if spike_percentage > rule.threshold_value:
                    self._create_alert(
                        rule_id=rule.id,
                        client_id=client_id,
                        service_name=rule.service_name,
                        alert_type='usage_spike',
                        current_value=current_usage,
                        expected_value=historical_avg,
                        deviation_percentage=spike_percentage,
                        message=f"Usage spike detected: {spike_percentage:.1f}% above normal"
                    )
    
    def _check_budget_projections(self, rule: AnomalyRule):
        """Project monthly spend and alert if budget will be exceeded"""
        current_date = datetime.utcnow()
        days_in_month = 30  # Simplified
        days_elapsed = current_date.day
        days_remaining = days_in_month - days_elapsed
        
        # Get current month usage
        month_start = current_date.replace(day=1, hour=0, minute=0, second=0)
        
        usage_by_service = db.session.query(
            APIUsage.service_name,
            func.sum(APIUsage.cost).label('total_cost')
        ).filter(
            APIUsage.timestamp >= month_start
        ).group_by(APIUsage.service_name).all()
        
        for service_name, current_cost in usage_by_service:
            # Get monthly budget from API config
            api_config = APIConfig.query.filter_by(service_name=service_name).first()
            if api_config and api_config.monthly_budget:
                # Project total monthly spend
                daily_average = current_cost / days_elapsed
                projected_total = current_cost + (daily_average * days_remaining)
                
                budget_usage_percentage = (projected_total / api_config.monthly_budget) * 100
                
                if budget_usage_percentage > rule.threshold_value:
                    self._create_alert(
                        rule_id=rule.id,
                        client_id=None,  # Platform-wide alert
                        service_name=service_name,
                        alert_type='budget_projection',
                        current_value=projected_total,
                        expected_value=api_config.monthly_budget,
                        deviation_percentage=budget_usage_percentage - 100,
                        message=f"Budget projection: {service_name} will exceed budget by {budget_usage_percentage - 100:.1f}%"
                    )
    
    def _check_pattern_deviations(self, rule: AnomalyRule):
        """Use ML to detect unusual usage patterns"""
        # Get current hour and day patterns
        current_hour = datetime.utcnow().hour
        current_day = datetime.utcnow().weekday()
        
        # Query historical patterns
        patterns = UsagePattern.query.filter_by(
            hour_of_day=current_hour,
            day_of_week=current_day
        ).all()
        
        for pattern in patterns:
            # Get current usage for this time slot
            current_usage = self._get_current_hour_usage(
                pattern.client_id, 
                pattern.service_name
            )
            
            # Calculate z-score
            if pattern.std_deviation > 0:
                z_score = abs((current_usage - pattern.average_usage) / pattern.std_deviation)
                
                # Alert if usage is more than 3 standard deviations away
                if z_score > 3:
                    deviation_percentage = ((current_usage - pattern.average_usage) / pattern.average_usage) * 100
                    
                    self._create_alert(
                        rule_id=rule.id,
                        client_id=pattern.client_id,
                        service_name=pattern.service_name,
                        alert_type='pattern_deviation',
                        current_value=current_usage,
                        expected_value=pattern.average_usage,
                        deviation_percentage=deviation_percentage,
                        message=f"Unusual usage pattern detected (z-score: {z_score:.2f})"
                    )
    
    def _create_alert(self, **kwargs):
        """Create alert if not in cooldown period"""
        # Check for recent similar alerts
        recent_alert = AnomalyAlert.query.filter_by(
            rule_id=kwargs['rule_id'],
            client_id=kwargs.get('client_id'),
            service_name=kwargs['service_name'],
            status='active'
        ).filter(
            AnomalyAlert.created_at >= datetime.utcnow() - timedelta(minutes=self.alert_cooldown)
        ).first()
        
        if not recent_alert:
            alert = AnomalyAlert(**kwargs)
            db.session.add(alert)
            db.session.commit()
            
            # Send notifications
            self._send_alert_notifications(alert)
    
    def _send_alert_notifications(self, alert: AnomalyAlert):
        """Send alert through multiple channels"""
        from services.admin_notification_service import AdminNotificationService
        
        notification_service = AdminNotificationService()
        
        # Determine priority based on alert type and deviation
        priority = 'high' if alert.deviation_percentage > 100 else 'medium'
        
        notification_service.send_notification(
            title=f"Cost Anomaly: {alert.alert_type}",
            message=alert.message,
            priority=priority,
            data={
                'alert_id': alert.id,
                'client_id': alert.client_id,
                'service': alert.service_name,
                'current_value': float(alert.current_value),
                'expected_value': float(alert.expected_value)
            }
        )
```

#### 1.3 API Endpoints
```python
# routes/admin/anomaly_detection.py
@admin_anomaly_bp.route('/api/admin/anomalies/rules', methods=['GET', 'POST'])
@admin_required
def manage_anomaly_rules():
    """Manage anomaly detection rules"""
    if request.method == 'GET':
        rules = AnomalyRule.query.all()
        return jsonify([rule.to_dict() for rule in rules])
    
    elif request.method == 'POST':
        data = request.get_json()
        rule = AnomalyRule(
            rule_type=data['rule_type'],
            service_name=data.get('service_name'),
            threshold_value=data['threshold_value'],
            threshold_type=data['threshold_type'],
            time_window=data.get('time_window', 60),
            severity=data.get('severity', 'warning')
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify(rule.to_dict()), 201

@admin_anomaly_bp.route('/api/admin/anomalies/alerts', methods=['GET'])
@admin_required
def get_anomaly_alerts():
    """Get anomaly alerts with filtering"""
    # Filter parameters
    status = request.args.get('status', 'active')
    client_id = request.args.get('client_id')
    service = request.args.get('service')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = AnomalyAlert.query
    
    if status:
        query = query.filter_by(status=status)
    if client_id:
        query = query.filter_by(client_id=client_id)
    if service:
        query = query.filter_by(service_name=service)
    if date_from:
        query = query.filter(AnomalyAlert.created_at >= date_from)
    if date_to:
        query = query.filter(AnomalyAlert.created_at <= date_to)
    
    alerts = query.order_by(AnomalyAlert.created_at.desc()).limit(100).all()
    return jsonify([alert.to_dict() for alert in alerts])

@admin_anomaly_bp.route('/api/admin/anomalies/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@admin_required
@audit_log
def acknowledge_alert(alert_id):
    """Acknowledge an anomaly alert"""
    alert = AnomalyAlert.query.get_or_404(alert_id)
    alert.status = 'acknowledged'
    alert.acknowledged_by = g.current_user.admin_profile.id
    alert.acknowledged_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'alert': alert.to_dict()})
```

---

## 2. 📋 Full Auditability Implementation

### Overview
Complete audit trail system with detailed logging, search capabilities, and compliance features.

### Audit Log Schema
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    -- Who
    user_id INTEGER REFERENCES users(id),
    user_role VARCHAR(20),
    user_email VARCHAR(255),
    admin_id INTEGER REFERENCES admins(id),
    
    -- What
    action_type VARCHAR(100) NOT NULL, -- 'create', 'update', 'delete', 'toggle', 'login', etc.
    action_category VARCHAR(50), -- 'platform', 'feature', 'client', 'config', 'security'
    action_description TEXT,
    
    -- Where/When
    resource_type VARCHAR(50), -- 'platform_config', 'feature_flag', 'client', etc.
    resource_id INTEGER,
    resource_name VARCHAR(255),
    
    -- Changes
    old_value JSONB,
    new_value JSONB,
    changed_fields TEXT[], -- Array of field names that changed
    
    -- Context
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_id UUID,
    session_id VARCHAR(255),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_sensitive BOOLEAN DEFAULT FALSE,
    compliance_flags JSONB, -- For regulatory compliance
    
    -- Indexing
    INDEX idx_audit_user (user_id, created_at),
    INDEX idx_audit_resource (resource_type, resource_id),
    INDEX idx_audit_action (action_type, created_at),
    INDEX idx_audit_admin (admin_id, created_at)
);

-- Audit log retention policy
CREATE TABLE audit_retention_policies (
    id SERIAL PRIMARY KEY,
    action_category VARCHAR(50),
    retention_days INTEGER NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE,
    archive_location VARCHAR(500)
);
```

### Enhanced Audit Service
```python
# services/audit_service.py
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from flask import request, g

class EnhancedAuditService:
    def __init__(self):
        self.sensitive_fields = ['password', 'api_key', 'secret', 'token']
    
    def log_action(
        self,
        action_type: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        description: Optional[str] = None
    ):
        """Log an administrative action with full context"""
        # Sanitize sensitive data
        if old_value:
            old_value = self._sanitize_data(old_value)
        if new_value:
            new_value = self._sanitize_data(new_value)
        
        # Calculate changed fields
        changed_fields = []
        if old_value and new_value:
            changed_fields = self._get_changed_fields(old_value, new_value)
        
        # Determine action category
        action_category = self._categorize_action(action_type, resource_type)
        
        # Check if this is a sensitive operation
        is_sensitive = self._is_sensitive_action(action_type, resource_type)
        
        # Create audit log entry
        audit_log = AuditLog(
            user_id=g.current_user.id,
            user_role=g.current_user.role,
            user_email=g.current_user.email,
            admin_id=g.current_user.admin_profile.id if g.current_user.role == 'admin' else None,
            action_type=action_type,
            action_category=action_category,
            action_description=description or self._generate_description(action_type, resource_type),
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=self._get_resource_name(resource_type, resource_id),
            old_value=old_value,
            new_value=new_value,
            changed_fields=changed_fields,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_id=g.request_id if hasattr(g, 'request_id') else None,
            session_id=g.session_id if hasattr(g, 'session_id') else None,
            is_sensitive=is_sensitive,
            compliance_flags=self._get_compliance_flags(action_type)
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        # Trigger real-time notifications for critical actions
        if is_sensitive or action_category == 'security':
            self._notify_security_team(audit_log)
        
        return audit_log
    
    def search_audit_logs(
        self,
        user_id: Optional[int] = None,
        admin_id: Optional[int] = None,
        action_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        text_search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Advanced search functionality for audit logs"""
        query = AuditLog.query
        
        # Apply filters
        if user_id:
            query = query.filter_by(user_id=user_id)
        if admin_id:
            query = query.filter_by(admin_id=admin_id)
        if action_type:
            query = query.filter_by(action_type=action_type)
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        if ip_address:
            query = query.filter_by(ip_address=ip_address)
        if date_from:
            query = query.filter(AuditLog.created_at >= date_from)
        if date_to:
            query = query.filter(AuditLog.created_at <= date_to)
        
        # Text search across description and changed fields
        if text_search:
            query = query.filter(
                db.or_(
                    AuditLog.action_description.ilike(f'%{text_search}%'),
                    AuditLog.resource_name.ilike(f'%{text_search}%'),
                    AuditLog.user_email.ilike(f'%{text_search}%')
                )
            )
        
        # Order by most recent first
        query = query.order_by(AuditLog.created_at.desc())
        
        # Apply pagination
        total = query.count()
        logs = query.limit(limit).offset(offset).all()
        
        return {
            'logs': logs,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    def _sanitize_data(self, data: Dict) -> Dict:
        """Remove sensitive fields from logged data"""
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def _get_changed_fields(self, old_value: Dict, new_value: Dict) -> List[str]:
        """Identify which fields changed between old and new values"""
        changed = []
        all_keys = set(old_value.keys()) | set(new_value.keys())
        
        for key in all_keys:
            old_val = old_value.get(key)
            new_val = new_value.get(key)
            if old_val != new_val:
                changed.append(key)
        
        return changed
    
    def export_audit_logs(self, filters: Dict, format: str = 'csv') -> str:
        """Export audit logs for compliance reporting"""
        logs = self.search_audit_logs(**filters)['logs']
        
        if format == 'csv':
            return self._export_to_csv(logs)
        elif format == 'json':
            return self._export_to_json(logs)
        elif format == 'pdf':
            return self._export_to_pdf(logs)
```

### Audit UI Component
```jsx
// components/AuditTrail.jsx
import React, { useState, useEffect } from 'react';
import { DateRangePicker } from './DateRangePicker';
import { DataTable } from './DataTable';
import { FilterPanel } from './FilterPanel';

const AuditTrail = () => {
    const [logs, setLogs] = useState([]);
    const [filters, setFilters] = useState({
        user_id: null,
        action_type: null,
        resource_type: null,
        date_from: null,
        date_to: null,
        text_search: ''
    });
    const [pagination, setPagination] = useState({
        limit: 50,
        offset: 0,
        total: 0
    });
    
    const fetchAuditLogs = async () => {
        const params = new URLSearchParams({
            ...filters,
            limit: pagination.limit,
            offset: pagination.offset
        });
        
        const response = await fetch(`/api/admin/audit-logs?${params}`);
        const data = await response.json();
        
        setLogs(data.logs);
        setPagination(prev => ({ ...prev, total: data.total }));
    };
    
    useEffect(() => {
        fetchAuditLogs();
    }, [filters, pagination.offset]);
    
    const columns = [
        {
            key: 'created_at',
            label: 'Timestamp',
            render: (value) => new Date(value).toLocaleString()
        },
        {
            key: 'user_email',
            label: 'User',
            render: (value, row) => (
                <div>
                    <div>{value}</div>
                    <small className="text-muted">{row.user_role}</small>
                </div>
            )
        },
        {
            key: 'action_type',
            label: 'Action',
            render: (value, row) => (
                <div>
                    <span className={`badge badge-${getActionColor(value)}`}>
                        {value}
                    </span>
                    <div className="small mt-1">{row.action_description}</div>
                </div>
            )
        },
        {
            key: 'resource_type',
            label: 'Resource',
            render: (value, row) => (
                <div>
                    <strong>{row.resource_name || `${value} #${row.resource_id}`}</strong>
                    <div className="small">
                        {row.changed_fields?.length > 0 && (
                            <span>Changed: {row.changed_fields.join(', ')}</span>
                        )}
                    </div>
                </div>
            )
        },
        {
            key: 'ip_address',
            label: 'IP Address',
            width: '120px'
        },
        {
            key: 'actions',
            label: 'Actions',
            render: (_, row) => (
                <button 
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => showDetails(row)}
                >
                    Details
                </button>
            )
        }
    ];
    
    return (
        <div className="audit-trail">
            <div className="audit-header">
                <h2>Audit Trail</h2>
                <div className="audit-actions">
                    <button className="btn btn-secondary" onClick={exportLogs}>
                        Export
                    </button>
                </div>
            </div>
            
            <FilterPanel onFilterChange={setFilters}>
                <input
                    type="text"
                    placeholder="Search logs..."
                    value={filters.text_search}
                    onChange={(e) => setFilters({...filters, text_search: e.target.value})}
                    className="form-control"
                />
                
                <select 
                    value={filters.action_type || ''}
                    onChange={(e) => setFilters({...filters, action_type: e.target.value})}
                    className="form-control"
                >
                    <option value="">All Actions</option>
                    <option value="create">Create</option>
                    <option value="update">Update</option>
                    <option value="delete">Delete</option>
                    <option value="toggle">Toggle</option>
                    <option value="login">Login</option>
                </select>
                
                <DateRangePicker
                    startDate={filters.date_from}
                    endDate={filters.date_to}
                    onChange={(start, end) => setFilters({
                        ...filters,
                        date_from: start,
                        date_to: end
                    })}
                />
            </FilterPanel>
            
            <DataTable
                columns={columns}
                data={logs}
                pagination={pagination}
                onPageChange={(offset) => setPagination({...pagination, offset})}
            />
        </div>
    );
};
```

---

## 3. 🔐 Granular Role Definitions

### Role Permission Matrix

```python
# config/permissions.py
ROLE_PERMISSIONS = {
    'support': {
        'clients': ['read'],
        'packages': ['read'],
        'features': ['read'],
        'platforms': ['read'],
        'analytics': ['read'],
        'audit_logs': ['read'],
        'api_keys': [],  # No access
        'ai_config': [],  # No access
        'pricing': [],  # No access
        'system_config': []  # No access
    },
    
    'admin': {
        'clients': ['create', 'read', 'update', 'delete', 'suspend', 'activate'],
        'packages': ['create', 'read', 'update', 'delete'],
        'features': ['read', 'toggle'],
        'platforms': ['read', 'toggle'],
        'analytics': ['read', 'export'],
        'audit_logs': ['read', 'export'],
        'api_keys': ['read'],  # Read-only
        'ai_config': ['read', 'update'],
        'pricing': ['read', 'update'],
        'system_config': ['read']
    },
    
    'owner': {
        # Unrestricted access - all permissions
        '*': ['*']
    }
}

# Additional fine-grained permissions
FEATURE_PERMISSIONS = {
    'support': {
        'view_client_dashboard': True,
        'impersonate_client': True,
        'modify_client_settings': False,
        'access_billing': False,
        'manage_api_keys': False,
        'system_maintenance': False
    },
    
    'admin': {
        'view_client_dashboard': True,
        'impersonate_client': True,
        'modify_client_settings': True,
        'access_billing': True,
        'manage_api_keys': False,  # Cannot modify
        'system_maintenance': True
    },
    
    'owner': {
        # All features enabled
        '_all': True
    }
}
```

### Permission Checking Service
```python
# services/permission_service.py
from functools import wraps
from flask import g, abort
from typing import List, Optional

class PermissionService:
    @staticmethod
    def check_permission(resource: str, action: str, user_role: Optional[str] = None) -> bool:
        """Check if a role has permission for an action on a resource"""
        role = user_role or g.current_user.role
        
        # Owner has all permissions
        if role == 'owner':
            return True
        
        # Check specific permissions
        role_perms = ROLE_PERMISSIONS.get(role, {})
        resource_perms = role_perms.get(resource, [])
        
        return action in resource_perms or '*' in resource_perms
    
    @staticmethod
    def check_feature(feature: str, user_role: Optional[str] = None) -> bool:
        """Check if a role has access to a specific feature"""
        role = user_role or g.current_user.role
        
        if role == 'owner':
            return True
        
        feature_perms = FEATURE_PERMISSIONS.get(role, {})
        return feature_perms.get(feature, False) or feature_perms.get('_all', False)

def require_permission(resource: str, action: str):
    """Decorator to check permissions before executing a function"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not PermissionService.check_permission(resource, action):
                abort(403, f"Insufficient permissions: {resource}:{action}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_feature(feature: str):
    """Decorator to check feature access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not PermissionService.check_feature(feature):
                abort(403, f"Feature not available: {feature}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## 4. 🚦 Third-Party API Status Dashboard

### API Health Monitoring System

```python
# services/api_health_service.py
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis

class APIHealthService:
    def __init__(self):
        self.redis_client = redis.Redis(decode_responses=True)
        self.check_interval = 300  # 5 minutes
        self.timeout = 10  # seconds
        
        self.api_endpoints = {
            'instagram': {
                'url': 'https://graph.instagram.com/v12.0/me',
                'method': 'GET',
                'headers': lambda: {'Authorization': f'Bearer {self.get_api_key("instagram")}'}
            },
            'snapchat': {
                'url': 'https://adsapi.snapchat.com/v1/me',
                'method': 'GET',
                'headers': lambda: {'Authorization': f'Bearer {self.get_api_key("snapchat")}'}
            },
            'openai': {
                'url': 'https://api.openai.com/v1/models',
                'method': 'GET',
                'headers': lambda: {'Authorization': f'Bearer {self.get_api_key("openai")}'}
            },
            'anthropic': {
                'url': 'https://api.anthropic.com/v1/messages',
                'method': 'GET',
                'headers': lambda: {'x-api-key': self.get_api_key("anthropic")}
            },
            'myfatoorah': {
                'url': 'https://api.myfatoorah.com/v2/GetPaymentStatus',
                'method': 'GET',
                'headers': lambda: {'Authorization': f'Bearer {self.get_api_key("myfatoorah")}'}
            },
            'prayer_times': {
                'url': 'http://api.aladhan.com/v1/timingsByCity?city=Kuwait&country=Kuwait',
                'method': 'GET',
                'headers': lambda: {}
            },
            'weather': {
                'url': 'https://api.openweathermap.org/data/2.5/weather?q=Kuwait',
                'method': 'GET',
                'headers': lambda: {'appid': self.get_api_key("openweather")}
            }
        }
    
    async def check_all_apis(self) -> Dict[str, Dict]:
        """Check health of all configured APIs"""
        results = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for api_name, config in self.api_endpoints.items():
                task = self.check_api_health(session, api_name, config)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for api_name, response in zip(self.api_endpoints.keys(), responses):
                if isinstance(response, Exception):
                    results[api_name] = {
                        'status': 'error',
                        'message': str(response),
                        'last_checked': datetime.utcnow().isoformat()
                    }
                else:
                    results[api_name] = response
        
        # Store results in Redis
        self._store_results(results)
        
        return results
    
    async def check_api_health(
        self, 
        session: aiohttp.ClientSession, 
        api_name: str, 
        config: Dict
    ) -> Dict:
        """Check health of a single API"""
        start_time = datetime.utcnow()
        
        try:
            headers = config['headers']()
            
            async with session.request(
                method=config['method'],
                url=config['url'],
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                status = 'healthy' if response.status < 400 else 'degraded'
                if response.status >= 500:
                    status = 'down'
                
                return {
                    'status': status,
                    'status_code': response.status,
                    'response_time': response_time,
                    'last_checked': datetime.utcnow().isoformat(),
                    'message': 'OK' if status == 'healthy' else f'HTTP {response.status}'
                }
                
        except asyncio.TimeoutError:
            return {
                'status': 'timeout',
                'response_time': self.timeout,
                'last_checked': datetime.utcnow().isoformat(),
                'message': 'Request timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'response_time': None,
                'last_checked': datetime.utcnow().isoformat(),
                'message': str(e)
            }
    
    def get_cached_status(self) -> Dict[str, Dict]:
        """Get cached API status from Redis"""
        cached = self.redis_client.get('api_health_status')
        if cached:
            return json.loads(cached)
        return {}
    
    def _store_results(self, results: Dict):
        """Store health check results in Redis"""
        self.redis_client.setex(
            'api_health_status',
            self.check_interval,
            json.dumps(results)
        )
        
        # Store historical data for trends
        for api_name, result in results.items():
            history_key = f'api_health_history:{api_name}'
            self.redis_client.lpush(history_key, json.dumps(result))
            self.redis_client.ltrim(history_key, 0, 288)  # Keep 24 hours of 5-min checks
```

### API Status Dashboard Component
```jsx
// components/APIStatusDashboard.jsx
import React, { useState, useEffect } from 'react';
import { StatusIndicator } from './StatusIndicator';
import { ResponseTimeChart } from './ResponseTimeChart';

const APIStatusDashboard = () => {
    const [apiStatus, setApiStatus] = useState({});
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);
    
    const fetchStatus = async () => {
        try {
            const response = await fetch('/api/admin/api-health');
            const data = await response.json();
            setApiStatus(data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch API status:', error);
        }
    };
    
    useEffect(() => {
        fetchStatus();
        
        if (autoRefresh) {
            const interval = setInterval(fetchStatus, 30000); // 30 seconds
            return () => clearInterval(interval);
        }
    }, [autoRefresh]);
    
    const getStatusColor = (status) => {
        switch (status) {
            case 'healthy': return 'success';
            case 'degraded': return 'warning';
            case 'down': return 'danger';
            case 'timeout': return 'warning';
            default: return 'secondary';
        }
    };
    
    const getOverallHealth = () => {
        const statuses = Object.values(apiStatus);
        if (statuses.every(s => s.status === 'healthy')) return 'All Systems Operational';
        if (statuses.some(s => s.status === 'down')) return 'Major Outage Detected';
        if (statuses.some(s => s.status === 'degraded')) return 'Partial Service Disruption';
        return 'Unknown';
    };
    
    return (
        <div className="api-status-dashboard">
            <div className="dashboard-header">
                <h3>Third-Party API Status</h3>
                <div className="dashboard-controls">
                    <label className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={autoRefresh}
                            onChange={(e) => setAutoRefresh(e.target.checked)}
                        />
                        <span>Auto-refresh</span>
                    </label>
                    <button 
                        className="btn btn-sm btn-secondary"
                        onClick={fetchStatus}
                        disabled={loading}
                    >
                        Refresh Now
                    </button>
                </div>
            </div>
            
            <div className={`overall-status alert alert-${
                getOverallHealth().includes('Operational') ? 'success' : 
                getOverallHealth().includes('Major') ? 'danger' : 'warning'
            }`}>
                <h4>{getOverallHealth()}</h4>
                <small>Last checked: {new Date().toLocaleString()}</small>
            </div>
            
            <div className="api-grid">
                {Object.entries(apiStatus).map(([apiName, status]) => (
                    <div key={apiName} className="api-card">
                        <div className="api-header">
                            <h5>{apiName.charAt(0).toUpperCase() + apiName.slice(1)}</h5>
                            <StatusIndicator 
                                status={status.status} 
                                color={getStatusColor(status.status)}
                            />
                        </div>
                        
                        <div className="api-details">
                            <div className="metric">
                                <span className="label">Status:</span>
                                <span className={`value text-${getStatusColor(status.status)}`}>
                                    {status.status}
                                </span>
                            </div>
                            
                            {status.response_time && (
                                <div className="metric">
                                    <span className="label">Response Time:</span>
                                    <span className="value">
                                        {(status.response_time * 1000).toFixed(0)}ms
                                    </span>
                                </div>
                            )}
                            
                            {status.status_code && (
                                <div className="metric">
                                    <span className="label">Status Code:</span>
                                    <span className="value">{status.status_code}</span>
                                </div>
                            )}
                            
                            <div className="metric">
                                <span className="label">Message:</span>
                                <span className="value small">{status.message}</span>
                            </div>
                        </div>
                        
                        <div className="api-actions">
                            <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => showAPIDetails(apiName)}
                            >
                                View History
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
```

---

## 5. 🔄 Enhanced JWT Authentication with Refresh Tokens

### Token Service Enhancement
```python
# services/auth_service.py
from datetime import datetime, timedelta
import jwt
import secrets
from typing import Dict, Optional, Tuple

class EnhancedAuthService:
    def __init__(self):
        self.access_token_expiry = timedelta(hours=2)
        self.refresh_token_expiry = timedelta(days=7)
        self.refresh_threshold = timedelta(minutes=30)  # Refresh if less than 30 min left
    
    def generate_token_pair(self, user) -> Dict[str, str]:
        """Generate both access and refresh tokens"""
        # Generate access token
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'exp': datetime.utcnow() + self.access_token_expiry,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        access_token = jwt.encode(
            access_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Generate refresh token
        refresh_token_id = secrets.token_urlsafe(32)
        refresh_payload = {
            'user_id': user.id,
            'token_id': refresh_token_id,
            'exp': datetime.utcnow() + self.refresh_token_expiry,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(
            refresh_payload,
            current_app.config['JWT_REFRESH_SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Store refresh token in database
        self._store_refresh_token(user.id, refresh_token_id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(self.access_token_expiry.total_seconds()),
            'refresh_expires_in': int(self.refresh_token_expiry.total_seconds())
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token using refresh token"""
        try:
            payload = jwt.decode(
                refresh_token,
                current_app.config['JWT_REFRESH_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Verify token type
            if payload.get('type') != 'refresh':
                return None
            
            # Check if refresh token is still valid in database
            if not self._is_refresh_token_valid(payload['user_id'], payload['token_id']):
                return None
            
            # Get user
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return None
            
            # Generate new access token only
            access_payload = {
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'exp': datetime.utcnow() + self.access_token_expiry,
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            access_token = jwt.encode(
                access_payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            return {
                'access_token': access_token,
                'expires_in': int(self.access_token_expiry.total_seconds())
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def should_refresh_token(self, token: str) -> bool:
        """Check if token should be refreshed (less than 30 min remaining)"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            exp = datetime.fromtimestamp(payload['exp'])
            time_remaining = exp - datetime.utcnow()
            
            return time_remaining < self.refresh_threshold
            
        except:
            return False
    
    def _store_refresh_token(self, user_id: int, token_id: str):
        """Store refresh token in database"""
        refresh_token = RefreshToken(
            user_id=user_id,
            token_id=token_id,
            expires_at=datetime.utcnow() + self.refresh_token_expiry,
            created_at=datetime.utcnow()
        )
        db.session.add(refresh_token)
        db.session.commit()
    
    def _is_refresh_token_valid(self, user_id: int, token_id: str) -> bool:
        """Check if refresh token exists and is valid"""
        token = RefreshToken.query.filter_by(
            user_id=user_id,
            token_id=token_id,
            is_revoked=False
        ).first()
        
        if not token:
            return False
        
        if token.expires_at < datetime.utcnow():
            return False
        
        return True
    
    def revoke_refresh_token(self, user_id: int, token_id: Optional[str] = None):
        """Revoke refresh tokens for a user"""
        query = RefreshToken.query.filter_by(user_id=user_id, is_revoked=False)
        
        if token_id:
            query = query.filter_by(token_id=token_id)
        
        query.update({'is_revoked': True})
        db.session.commit()
```

### Frontend Token Management
```javascript
// services/authService.js
class AuthService {
    constructor() {
        this.refreshInterval = null;
        this.refreshThreshold = 30 * 60 * 1000; // 30 minutes in ms
    }
    
    async login(email, password) {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            this.storeTokens(data);
            this.setupTokenRefresh();
            return data;
        }
        
        throw new Error(data.error || 'Login failed');
    }
    
    storeTokens(data) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('token_expires', Date.now() + (data.expires_in * 1000));
    }
    
    setupTokenRefresh() {
        // Clear any existing interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Check token every minute
        this.refreshInterval = setInterval(() => {
            this.checkAndRefreshToken();
        }, 60000); // 1 minute
        
        // Also check immediately
        this.checkAndRefreshToken();
    }
    
    async checkAndRefreshToken() {
        const tokenExpires = localStorage.getItem('token_expires');
        if (!tokenExpires) return;
        
        const timeRemaining = parseInt(tokenExpires) - Date.now();
        
        // Refresh if less than 30 minutes remaining
        if (timeRemaining < this.refreshThreshold) {
            await this.refreshToken();
        }
    }
    
    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            this.logout();
            return;
        }
        
        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('token_expires', Date.now() + (data.expires_in * 1000));
                
                // Emit event for other components
                window.dispatchEvent(new Event('tokenRefreshed'));
            } else {
                // Refresh failed, logout
                this.logout();
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.logout();
        }
    }
    
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token_expires');
        
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Redirect to login
        window.location.href = '/login';
    }
    
    getAuthHeader() {
        const token = localStorage.getItem('access_token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }
}

export default new AuthService();
```

---

## 6. 👤 Admin Impersonation Mode

### Impersonation Service
```python
# services/impersonation_service.py
from datetime import datetime, timedelta
from typing import Optional, Dict
import secrets
from flask import g, session

class ImpersonationService:
    def __init__(self):
        self.max_duration = timedelta(hours=1)
        self.allowed_roles = ['admin', 'support', 'owner']
    
    def start_impersonation(
        self, 
        admin_user, 
        client_id: int, 
        reason: str
    ) -> Optional[Dict]:
        """Start impersonating a client"""
        # Check permissions
        if admin_user.role not in self.allowed_roles:
            return None
        
        # Get client
        client = Client.query.get(client_id)
        if not client:
            return None
        
        # Generate impersonation token
        impersonation_id = secrets.token_urlsafe(32)
        
        # Create impersonation record
        impersonation = Impersonation(
            id=impersonation_id,
            admin_id=admin_user.id,
            client_id=client_id,
            reason=reason,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.max_duration,
            ip_address=request.remote_addr
        )
        db.session.add(impersonation)
        db.session.commit()
        
        # Log the action
        audit_service.log_action(
            action_type='impersonation_start',
            resource_type='client',
            resource_id=client_id,
            description=f'Started impersonating client: {client.business_name}'
        )
        
        # Generate special JWT for impersonation
        token_payload = {
            'user_id': client.user_id,
            'email': client.email,
            'role': 'client',
            'impersonation': {
                'admin_id': admin_user.id,
                'admin_email': admin_user.email,
                'impersonation_id': impersonation_id,
                'expires_at': impersonation.expires_at.isoformat()
            },
            'exp': impersonation.expires_at
        }
        
        impersonation_token = jwt.encode(
            token_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return {
            'impersonation_id': impersonation_id,
            'token': impersonation_token,
            'client': {
                'id': client.id,
                'business_name': client.business_name,
                'email': client.email
            },
            'expires_at': impersonation.expires_at.isoformat()
        }
    
    def end_impersonation(self, impersonation_id: str) -> bool:
        """End an active impersonation session"""
        impersonation = Impersonation.query.get(impersonation_id)
        if not impersonation or impersonation.ended_at:
            return False
        
        impersonation.ended_at = datetime.utcnow()
        db.session.commit()
        
        # Log the action
        audit_service.log_action(
            action_type='impersonation_end',
            resource_type='client',
            resource_id=impersonation.client_id,
            description='Ended impersonation session'
        )
        
        return True
    
    def is_impersonating(self) -> bool:
        """Check if current request is an impersonation"""
        return hasattr(g, 'impersonation') and g.impersonation is not None
    
    def get_impersonation_info(self) -> Optional[Dict]:
        """Get current impersonation details"""
        if not self.is_impersonating():
            return None
        
        return {
            'admin_id': g.impersonation.get('admin_id'),
            'admin_email': g.impersonation.get('admin_email'),
            'impersonation_id': g.impersonation.get('impersonation_id'),
            'expires_at': g.impersonation.get('expires_at')
        }
```

### Impersonation UI Component
```jsx
// components/ImpersonationMode.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

const ImpersonationMode = () => {
    const { isImpersonating, impersonationInfo, endImpersonation } = useAuth();
    const [timeRemaining, setTimeRemaining] = useState(null);
    
    useEffect(() => {
        if (impersonationInfo?.expires_at) {
            const interval = setInterval(() => {
                const remaining = new Date(impersonationInfo.expires_at) - new Date();
                if (remaining > 0) {
                    setTimeRemaining(Math.floor(remaining / 1000));
                } else {
                    endImpersonation();
                }
            }, 1000);
            
            return () => clearInterval(interval);
        }
    }, [impersonationInfo]);
    
    if (!isImpersonating) return null;
    
    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    };
    
    return (
        <div className="impersonation-banner">
            <div className="impersonation-content">
                <span className="impersonation-icon">👤</span>
                <span className="impersonation-text">
                    Viewing as: <strong>{impersonationInfo.client.business_name}</strong>
                </span>
                <span className="impersonation-admin">
                    (Admin: {impersonationInfo.admin_email})
                </span>
                {timeRemaining && (
                    <span className="impersonation-timer">
                        Time remaining: {formatTime(timeRemaining)}
                    </span>
                )}
                <button 
                    className="btn btn-sm btn-warning"
                    onClick={endImpersonation}
                >
                    End Impersonation
                </button>
            </div>
        </div>
    );
};

// Client selector for starting impersonation
const ClientImpersonationSelector = () => {
    const [clients, setClients] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [reason, setReason] = useState('');
    const [selectedClient, setSelectedClient] = useState(null);
    
    const startImpersonation = async () => {
        if (!selectedClient || !reason) {
            alert('Please select a client and provide a reason');
            return;
        }
        
        try {
            const response = await fetch('/api/admin/impersonate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...authService.getAuthHeader()
                },
                body: JSON.stringify({
                    client_id: selectedClient.id,
                    reason: reason
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                // Store impersonation token and redirect
                localStorage.setItem('impersonation_token', data.token);
                window.location.href = '/client/dashboard';
            }
        } catch (error) {
            console.error('Failed to start impersonation:', error);
        }
    };
    
    return (
        <div className="impersonation-selector">
            <h3>View as Client</h3>
            <p className="text-muted">
                This allows you to see exactly what a client sees in their dashboard.
            </p>
            
            <div className="form-group">
                <input
                    type="text"
                    className="form-control"
                    placeholder="Search clients..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>
            
            <div className="client-list">
                {clients
                    .filter(c => 
                        c.business_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        c.email.toLowerCase().includes(searchTerm.toLowerCase())
                    )
                    .map(client => (
                        <div 
                            key={client.id}
                            className={`client-item ${selectedClient?.id === client.id ? 'selected' : ''}`}
                            onClick={() => setSelectedClient(client)}
                        >
                            <div className="client-info">
                                <strong>{client.business_name}</strong>
                                <small>{client.email}</small>
                            </div>
                            <span className={`status-badge ${client.status}`}>
                                {client.status}
                            </span>
                        </div>
                    ))
                }
            </div>
            
            <div className="form-group">
                <label>Reason for impersonation:</label>
                <textarea
                    className="form-control"
                    rows="3"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="e.g., Troubleshooting reported issue with scheduling..."
                />
            </div>
            
            <button 
                className="btn btn-primary"
                onClick={startImpersonation}
                disabled={!selectedClient || !reason}
            >
                Start Impersonation
            </button>
            
            <div className="impersonation-warning">
                <strong>⚠️ Important:</strong> All actions taken during impersonation 
                are logged and attributed to your admin account.
            </div>
        </div>
    );
};
```

---

## 7. ❓ In-App Contextual Help

### Help System Implementation
```jsx
// components/ContextualHelp.jsx
import React, { useState } from 'react';
import { Popover } from './Popover';

const HelpIcon = ({ topic, content, link }) => {
    const [showHelp, setShowHelp] = useState(false);
    
    return (
        <div className="help-icon-wrapper">
            <button
                className="help-icon"
                onClick={() => setShowHelp(!showHelp)}
                aria-label={`Help for ${topic}`}
            >
                ?
            </button>
            
            <Popover
                isOpen={showHelp}
                onClose={() => setShowHelp(false)}
                position="right"
            >
                <div className="help-content">
                    <h5>{topic}</h5>
                    <p>{content}</p>
                    {link && (
                        <a 
                            href={link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="help-link"
                        >
                            Learn more →
                        </a>
                    )}
                </div>
            </Popover>
        </div>
    );
};

// Help content definitions
const helpContent = {
    prayer_time_settings: {
        topic: "Prayer Time Settings",
        content: "Automatically pause all social media posts during prayer times. You can configure the pause duration and choose which prayers to observe. Friday prayers have an extended pause option for Jummah.",
        link: "/docs/kuwait-features#prayer-times"
    },
    
    ai_budget: {
        topic: "AI Service Budget",
        content: "Set monthly spending limits for each AI service. The system will alert you when usage reaches 75% and 90% of the budget. Projected overages are calculated based on current usage patterns.",
        link: "/docs/ai-services#budgets"
    },
    
    weather_strategies: {
        topic: "Weather-Based Content",
        content: "Content automatically adapts to Kuwait's weather. When temperatures exceed 45°C, the system promotes indoor dining and delivery. Sandstorm alerts pause outdoor-focused content.",
        link: "/docs/kuwait-features#weather"
    },
    
    feature_flags: {
        topic: "Feature Management",
        content: "Control which features are available to clients. Changes take effect immediately across all client dashboards. You can enable features globally or per package.",
        link: "/docs/admin-features#feature-flags"
    },
    
    platform_health: {
        topic: "API Health Monitoring",
        content: "Real-time status of all third-party services. Green = operational, Yellow = degraded performance, Red = service down. Historical data shows patterns and helps diagnose issues.",
        link: "/docs/monitoring#api-health"
    },
    
    anomaly_detection: {
        topic: "Cost Anomaly Detection",
        content: "AI monitors usage patterns and alerts you to unusual spikes or projected budget overruns. Alerts are based on historical patterns and configurable thresholds.",
        link: "/docs/monitoring#anomaly-detection"
    }
};

// Usage in components
const KuwaitSettingsPanel = () => {
    return (
        <div className="settings-panel">
            <div className="setting-header">
                <h3>Prayer Time Configuration</h3>
                <HelpIcon {...helpContent.prayer_time_settings} />
            </div>
            {/* Settings content */}
        </div>
    );
};

const AIBudgetPanel = () => {
    return (
        <div className="budget-panel">
            <div className="budget-header">
                <h3>Monthly AI Budget</h3>
                <HelpIcon {...helpContent.ai_budget} />
            </div>
            {/* Budget controls */}
        </div>
    );
};
```

### Help Content Management
```python
# services/help_content_service.py
class HelpContentService:
    def __init__(self):
        self.help_topics = {
            'prayer_time_settings': {
                'title': 'Prayer Time Settings',
                'content': '''
                    Automatically pause all social media posts during prayer times.
                    - Configure pause duration (15-30 minutes)
                    - Choose which prayers to observe
                    - Friday extended pause for Jummah
                    - Notifications before prayer times
                ''',
                'video_url': '/help/videos/prayer-settings.mp4',
                'related_topics': ['kuwait_features', 'scheduling'],
                'category': 'kuwait_specific'
            },
            # ... more help topics
        }
    
    def get_help_content(self, topic_id: str, user_role: str = None) -> Dict:
        """Get help content for a specific topic"""
        content = self.help_topics.get(topic_id)
        if not content:
            return None
        
        # Filter content based on user role if needed
        if user_role and content.get('min_role'):
            if not self._has_role_access(user_role, content['min_role']):
                return None
        
        # Track help usage for analytics
        self._track_help_usage(topic_id, user_role)
        
        return content
    
    def search_help(self, query: str) -> List[Dict]:
        """Search help content"""
        results = []
        query_lower = query.lower()
        
        for topic_id, content in self.help_topics.items():
            score = 0
            
            # Title match
            if query_lower in content['title'].lower():
                score += 10
            
            # Content match
            if query_lower in content['content'].lower():
                score += 5
            
            # Category match
            if query_lower in content.get('category', '').lower():
                score += 3
            
            if score > 0:
                results.append({
                    'topic_id': topic_id,
                    'title': content['title'],
                    'snippet': content['content'][:150] + '...',
                    'score': score
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:10]
```

---

## 📊 Implementation Summary

These enhancements transform the admin panel from a basic control interface to a **proactive, intelligent management system**:

1. **Cost Management**: From passive monitoring to predictive alerts
2. **Audit Trail**: Complete accountability with searchable history
3. **Security**: Granular permissions and secure authentication
4. **Reliability**: Real-time API health monitoring
5. **User Experience**: Smooth workflows with impersonation and help
6. **Performance**: Non-disruptive token refresh

### Priority Implementation Order:
1. **Week 1**: Audit system and granular permissions
2. **Week 2**: Cost anomaly detection
3. **Week 3**: API health dashboard and JWT refresh
4. **Week 4**: Impersonation mode and contextual help

These features ensure the admin panel is not just functional but **exceptional** in supporting platform growth and reliability.