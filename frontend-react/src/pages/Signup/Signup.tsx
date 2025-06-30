import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiClient } from '../../services/api/apiClient';
import './Signup.css';

interface SignupFormData {
  companyName: string;
  contactName: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}

const Signup: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<SignupFormData>({
    companyName: '',
    contactName: '',
    email: '',
    phone: '+965',
    password: '',
    confirmPassword: '',
    acceptTerms: false
  });
  const [errors, setErrors] = useState<Partial<SignupFormData>>({});

  const validateStep = (step: number): boolean => {
    const newErrors: Partial<SignupFormData> = {};

    switch (step) {
      case 1:
        if (!formData.companyName) newErrors.companyName = 'Company name is required';
        if (!formData.contactName) newErrors.contactName = 'Contact name is required';
        break;
      case 2:
        if (!formData.email) {
          newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
          newErrors.email = 'Invalid email format';
        }
        if (!formData.phone || formData.phone.length < 12) {
          newErrors.phone = 'Valid Kuwait phone number required';
        }
        break;
      case 3:
        if (!formData.password) {
          newErrors.password = 'Password is required';
        } else if (formData.password.length < 8) {
          newErrors.password = 'Password must be at least 8 characters';
        }
        if (formData.password !== formData.confirmPassword) {
          newErrors.confirmPassword = 'Passwords do not match';
        }
        if (!formData.acceptTerms) {
          newErrors.acceptTerms = 'You must accept the terms and conditions';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      if (currentStep < 3) {
        setCurrentStep(currentStep + 1);
      } else {
        handleSubmit();
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    // Clear error when user starts typing
    if (errors[name as keyof SignupFormData]) {
      setErrors({
        ...errors,
        [name]: undefined
      });
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await apiClient.post('/api/auth/register', {
        email: formData.email,
        password: formData.password,
        company_name: formData.companyName,
        contact_name: formData.contactName,
        phone: formData.phone,
        address: '' // Optional field
      });

      if (response.data.access_token) {
        // Registration successful - could auto-login or redirect
        alert('Registration successful! Please login with your credentials.');
        navigate('/login');
      }
    } catch (error: any) {
      console.error('Signup failed:', error);
      if (error.response?.data?.error) {
        alert(`Registration failed: ${error.response.data.error}`);
      } else {
        alert('Registration failed. Please try again.');
      }
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="form-step">
            <h2>Business Information</h2>
            <div className="form-group">
              <label htmlFor="companyName">Restaurant/Company Name *</label>
              <input
                type="text"
                id="companyName"
                name="companyName"
                value={formData.companyName}
                onChange={handleInputChange}
                className={errors.companyName ? 'error' : ''}
                placeholder="e.g., Kuwait Coffee House"
              />
              {errors.companyName && <span className="error-message">{errors.companyName}</span>}
            </div>
            <div className="form-group">
              <label htmlFor="contactName">Contact Person Name *</label>
              <input
                type="text"
                id="contactName"
                name="contactName"
                value={formData.contactName}
                onChange={handleInputChange}
                className={errors.contactName ? 'error' : ''}
                placeholder="Your full name"
              />
              {errors.contactName && <span className="error-message">{errors.contactName}</span>}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="form-step">
            <h2>Contact Details</h2>
            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={errors.email ? 'error' : ''}
                placeholder="your@email.com"
              />
              {errors.email && <span className="error-message">{errors.email}</span>}
            </div>
            <div className="form-group">
              <label htmlFor="phone">Kuwait Phone Number *</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className={errors.phone ? 'error' : ''}
                placeholder="+965 XXXX XXXX"
              />
              {errors.phone && <span className="error-message">{errors.phone}</span>}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="form-step">
            <h2>Create Password</h2>
            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={errors.password ? 'error' : ''}
                placeholder="Minimum 8 characters"
              />
              {errors.password && <span className="error-message">{errors.password}</span>}
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password *</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={errors.confirmPassword ? 'error' : ''}
                placeholder="Re-enter your password"
              />
              {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="acceptTerms"
                  checked={formData.acceptTerms}
                  onChange={handleInputChange}
                />
                I accept the <a href="/terms" target="_blank">Terms and Conditions</a> and <a href="/privacy" target="_blank">Privacy Policy</a>
              </label>
              {errors.acceptTerms && <span className="error-message">{errors.acceptTerms}</span>}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-container">
        <div className="signup-header">
          <Link to="/" className="logo">Kuwait Social AI</Link>
          <h1>Start Your Free Trial</h1>
          <p>Join Kuwait's leading F&B social media platform</p>
        </div>

        {/* Progress Indicator */}
        <div className="progress-indicator">
          <div className={`step ${currentStep >= 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
            <div className="step-number">1</div>
            <div className="step-label">Business Info</div>
          </div>
          <div className={`step ${currentStep >= 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
            <div className="step-number">2</div>
            <div className="step-label">Contact Details</div>
          </div>
          <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
            <div className="step-number">3</div>
            <div className="step-label">Create Password</div>
          </div>
        </div>

        {/* Form Steps */}
        <form className="signup-form" onSubmit={(e) => e.preventDefault()}>
          {renderStep()}

          {/* Navigation Buttons */}
          <div className="form-navigation">
            {currentStep > 1 && (
              <button type="button" className="btn btn-secondary" onClick={handlePrevious}>
                Previous
              </button>
            )}
            <button type="button" className="btn btn-primary" onClick={handleNext}>
              {currentStep === 3 ? 'Complete Signup' : 'Next'}
            </button>
          </div>
        </form>

        <div className="signup-footer">
          <p>Already have an account? <Link to="/login">Login here</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Signup;