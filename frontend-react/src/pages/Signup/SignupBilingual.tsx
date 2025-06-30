import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { apiClient } from '../../services/api/apiClient';
import { LanguageSwitcher } from '../../components/common/LanguageSwitcher';
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

const SignupBilingual: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
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

  // Get plan details with translations
  const getPlanDetails = (planKey: string) => {
    const plans = {
      basic: {
        name: t('landing.pricing.plans.basic.name'),
        price: `10 ${t('landing.pricing.currency')}${t('landing.pricing.per_month')}`,
        features: t('landing.pricing.plans.basic.features', { returnObjects: true }) as string[]
      },
      professional: {
        name: t('landing.pricing.plans.professional.name'),
        price: `15 ${t('landing.pricing.currency')}${t('landing.pricing.per_month')}`,
        features: t('landing.pricing.plans.professional.features', { returnObjects: true }) as string[]
      },
      premium: {
        name: t('landing.pricing.plans.premium.name'),
        price: `49 ${t('landing.pricing.currency')}${t('landing.pricing.per_month')}`,
        features: t('landing.pricing.plans.premium.features', { returnObjects: true }) as string[]
      }
    };
    return plans[planKey as keyof typeof plans] || plans.professional;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(''); // Clear error on input change
  };

  const validateForm = (): boolean => {
    // Basic validation
    if (!formData.email || !formData.password || !formData.companyName || !formData.contactName || !formData.phone) {
      setError(t('auth.signup.errors.allFieldsRequired'));
      return false;
    }

    // Email validation
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError(t('auth.signup.errors.invalidEmail'));
      return false;
    }

    // Password validation
    if (formData.password.length < 8) {
      setError(t('auth.signup.errors.weakPassword'));
      return false;
    }

    // Strong password requirements
    if (!/[A-Z]/.test(formData.password)) {
      setError(t('auth.signup.errors.passwordRequirements.uppercase'));
      return false;
    }
    if (!/[a-z]/.test(formData.password)) {
      setError(t('auth.signup.errors.passwordRequirements.lowercase'));
      return false;
    }
    if (!/[0-9]/.test(formData.password)) {
      setError(t('auth.signup.errors.passwordRequirements.number'));
      return false;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.password)) {
      setError(t('auth.signup.errors.passwordRequirements.special'));
      return false;
    }

    // Confirm password
    if (formData.password !== formData.confirmPassword) {
      setError(t('auth.signup.errors.passwordMismatch'));
      return false;
    }

    // Phone validation (Kuwait format)
    if (!/^\+965[0-9]{7,8}$/.test(formData.phone)) {
      setError(t('auth.signup.errors.invalidPhone'));
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
        requested_plan: formData.selectedPlan,
        address: ''
      });

      if (response.data) {
        // Registration successful
        const planName = getPlanDetails(formData.selectedPlan).name;
        alert(t('auth.signup.success', { plan: planName }));
        navigate('/login');
      }
    } catch (error: any) {
      console.error('Signup failed:', error);
      if (error.response?.data?.error) {
        // Translate common backend errors
        const backendError = error.response.data.error;
        if (backendError.includes('already exists') || backendError.includes('already registered')) {
          setError(t('auth.signup.errors.emailExists'));
        } else {
          setError(backendError);
        }
      } else if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else {
        setError(t('auth.signup.errors.serverError'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`signup-page ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="signup-container">
        <div className="signup-header">
          <div className="header-top">
            <Link to="/" className="logo">{t('common.appName')}</Link>
            <LanguageSwitcher />
          </div>
          <h1>{t('auth.signup.title')}</h1>
          <p>{t('auth.signup.subtitle')}</p>
        </div>

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <form className="signup-form" onSubmit={handleSubmit}>
          {/* Plan Selection */}
          <div className="plan-selection-section">
            <h3>{t('auth.signup.selectPlan')}</h3>
            <div className="plan-options">
              {['basic', 'professional', 'premium'].map((planKey) => {
                const plan = getPlanDetails(planKey);
                return (
                  <div 
                    key={planKey} 
                    className={`plan-option ${formData.selectedPlan === planKey ? 'selected' : ''}`}
                    onClick={() => setFormData(prev => ({ ...prev, selectedPlan: planKey }))}
                  >
                    <input
                      type="radio"
                      id={`plan-${planKey}`}
                      name="selectedPlan"
                      value={planKey}
                      checked={formData.selectedPlan === planKey}
                      onChange={handleInputChange}
                    />
                    <label htmlFor={`plan-${planKey}`}>
                      <div className="plan-name">{plan.name}</div>
                      <div className="plan-price">{plan.price}</div>
                      <ul className="plan-features-mini">
                        {plan.features.slice(0, 3).map((feature, idx) => (
                          <li key={idx}>{feature}</li>
                        ))}
                      </ul>
                    </label>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="companyName">{t('auth.signup.companyName')} *</label>
            <input
              type="text"
              id="companyName"
              name="companyName"
              value={formData.companyName}
              onChange={handleInputChange}
              placeholder={t('auth.signup.companyNamePlaceholder')}
              disabled={loading}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </div>

          <div className="form-group">
            <label htmlFor="contactName">{t('auth.signup.contactName')} *</label>
            <input
              type="text"
              id="contactName"
              name="contactName"
              value={formData.contactName}
              onChange={handleInputChange}
              placeholder={t('auth.signup.contactNamePlaceholder')}
              disabled={loading}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">{t('auth.signup.email')} *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder={t('auth.signup.emailPlaceholder')}
              disabled={loading}
              dir="ltr"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">{t('auth.signup.phone')} *</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              placeholder={t('auth.signup.phonePlaceholder')}
              disabled={loading}
              dir="ltr"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              {t('auth.signup.password')} * 
              <span className="password-hint">
                {t('auth.signup.passwordHint')}
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
              dir="ltr"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">{t('auth.signup.confirmPassword')} *</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              placeholder="••••••••"
              disabled={loading}
              dir="ltr"
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary submit-btn" 
            disabled={loading}
          >
            {loading 
              ? t('auth.signup.submitting') 
              : t('auth.signup.submit', { plan: getPlanDetails(formData.selectedPlan).name })
            }
          </button>
        </form>

        <div className="signup-footer">
          <p>
            {t('auth.signup.terms')}{' '}
            <a href="/terms" target="_blank">{t('auth.signup.termsLink')}</a>{' '}
            {t('auth.signup.and')}{' '}
            <a href="/privacy" target="_blank">{t('auth.signup.privacyLink')}</a>
          </p>
          <p>
            {t('auth.signup.haveAccount')}{' '}
            <Link to="/login">{t('auth.signup.loginLink')}</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupBilingual;