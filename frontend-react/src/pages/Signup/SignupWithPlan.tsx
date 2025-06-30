import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { apiClient } from '../../services/api/apiClient';
import './Signup.css';

interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
  companyName: string;
  contactName: string;
  phone: string;
  selectedPlan: string;
}

interface PlanDetails {
  name: string;
  price: string;
  features: string[];
}

const SignupWithPlan: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    companyName: '',
    contactName: '',
    phone: '+965',
    selectedPlan: searchParams.get('plan') || 'professional'
  });

  const plans: Record<string, PlanDetails> = {
    basic: {
      name: 'Basic',
      price: '10 KWD/mo',
      features: [
        '50 AI-generated posts',
        'Basic templates',
        'Email support',
        'Instagram integration'
      ]
    },
    professional: {
      name: 'Professional',
      price: '15 KWD/mo',
      features: [
        '100 AI-generated posts',
        'Advanced templates',
        'Image enhancement',
        'Priority support',
        'Analytics dashboard'
      ]
    },
    premium: {
      name: 'Premium',
      price: '49 KWD/mo',
      features: [
        '500 AI-generated posts',
        'Custom templates',
        'Team collaboration',
        'API access',
        'Dedicated support'
      ]
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(''); // Clear error on input change
  };

  const validateForm = (): boolean => {
    // Basic validation
    if (!formData.email || !formData.password || !formData.companyName || !formData.contactName || !formData.phone) {
      setError('All fields are required');
      return false;
    }

    // Email validation
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError('Invalid email format');
      return false;
    }

    // Password validation
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }

    // Strong password requirements
    if (!/[A-Z]/.test(formData.password)) {
      setError('Password must contain at least one uppercase letter');
      return false;
    }
    if (!/[a-z]/.test(formData.password)) {
      setError('Password must contain at least one lowercase letter');
      return false;
    }
    if (!/[0-9]/.test(formData.password)) {
      setError('Password must contain at least one number');
      return false;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.password)) {
      setError('Password must contain at least one special character');
      return false;
    }

    // Confirm password
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    // Phone validation (Kuwait format)
    if (!/^\+965[0-9]{7,8}$/.test(formData.phone)) {
      setError('Invalid Kuwait phone number. Format: +965XXXXXXXX');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await apiClient.post('/api/auth/register', {
        email: formData.email,
        password: formData.password,
        company_name: formData.companyName,
        contact_name: formData.contactName,
        phone: formData.phone,
        requested_plan: formData.selectedPlan, // Include selected plan
        address: ''
      });

      if (response.data) {
        // Registration successful
        alert(`Registration successful! Your account is pending approval. You selected the ${plans[formData.selectedPlan].name} plan. We will contact you soon.`);
        navigate('/login');
      }
    } catch (error: any) {
      console.error('Signup failed:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-container">
        <div className="signup-header">
          <Link to="/" className="logo">Kuwait Social AI</Link>
          <h1>Create Your Account</h1>
          <p>Join Kuwait's leading F&B social media platform</p>
        </div>

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <form className="signup-form" onSubmit={handleSubmit}>
          {/* Plan Selection */}
          <div className="plan-selection-section">
            <h3>Select Your Plan</h3>
            <div className="plan-options">
              {Object.entries(plans).map(([key, plan]) => (
                <div 
                  key={key} 
                  className={`plan-option ${formData.selectedPlan === key ? 'selected' : ''}`}
                  onClick={() => setFormData(prev => ({ ...prev, selectedPlan: key }))}
                >
                  <input
                    type="radio"
                    id={`plan-${key}`}
                    name="selectedPlan"
                    value={key}
                    checked={formData.selectedPlan === key}
                    onChange={handleInputChange}
                  />
                  <label htmlFor={`plan-${key}`}>
                    <div className="plan-name">{plan.name}</div>
                    <div className="plan-price">{plan.price}</div>
                    <ul className="plan-features-mini">
                      {plan.features.slice(0, 3).map((feature, idx) => (
                        <li key={idx}>{feature}</li>
                      ))}
                    </ul>
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="companyName">Restaurant/Company Name *</label>
            <input
              type="text"
              id="companyName"
              name="companyName"
              value={formData.companyName}
              onChange={handleInputChange}
              placeholder="e.g., Kuwait Coffee House"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="contactName">Your Full Name *</label>
            <input
              type="text"
              id="contactName"
              name="contactName"
              value={formData.contactName}
              onChange={handleInputChange}
              placeholder="John Doe"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="your@email.com"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Kuwait Phone Number *</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              placeholder="+965 XXXX XXXX"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password * 
              <span className="password-hint">
                (8+ chars, uppercase, lowercase, number, special char)
              </span>
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password *</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary submit-btn" 
            disabled={loading}
          >
            {loading ? 'Creating Account...' : `Sign Up for ${plans[formData.selectedPlan].name} Plan`}
          </button>
        </form>

        <div className="signup-footer">
          <p>
            By signing up, you agree to our{' '}
            <a href="/terms" target="_blank">Terms of Service</a> and{' '}
            <a href="/privacy" target="_blank">Privacy Policy</a>
          </p>
          <p>Already have an account? <Link to="/login">Login here</Link></p>
        </div>
      </div>
    </div>
  );
};

export default SignupWithPlan;