import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from '../../components/common/LanguageSwitcher';
import './Landing.css';

const LandingBilingual: React.FC = () => {
  const navigate = useNavigate();
  const { t, i18n, ready } = useTranslation();
  const isRTL = i18n.language === 'ar';


  // Show loading state while translations are loading
  if (!ready) {
    return (
      <div className="landing-page">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <div>Loading translations...</div>
        </div>
      </div>
    );
  }

  const features = [
    {
      icon: '🍔',
      titleKey: 'landing.features.items.specialist.title',
      descriptionKey: 'landing.features.items.specialist.description'
    },
    {
      icon: '📸',
      titleKey: 'landing.features.items.photography.title',
      descriptionKey: 'landing.features.items.photography.description'
    },
    {
      icon: '🌙',
      titleKey: 'landing.features.items.holidays.title',
      descriptionKey: 'landing.features.items.holidays.description'
    },
    {
      icon: '🏷️',
      titleKey: 'landing.features.items.promotions.title',
      descriptionKey: 'landing.features.items.promotions.description'
    },
    {
      icon: '⭐',
      titleKey: 'landing.features.items.reviews.title',
      descriptionKey: 'landing.features.items.reviews.description'
    },
    {
      icon: '📊',
      titleKey: 'landing.features.items.insights.title',
      descriptionKey: 'landing.features.items.insights.description'
    }
  ];

  // Default features to prevent errors
  const defaultFeatures = {
    basic: ["50 AI-generated posts", "Basic templates", "Email support", "Instagram integration"],
    professional: ["100 AI-generated posts", "Advanced templates", "Image enhancement", "Priority support", "Analytics dashboard"],
    premium: ["500 AI-generated posts", "Custom templates", "Team collaboration", "API access", "Dedicated support"]
  };

  const plans = [
    {
      name: t('landing.pricing.plans.basic.name', 'Basic'),
      price: `10 ${t('landing.pricing.currency', 'KWD')}${t('landing.pricing.per_month', '/mo')}`,
      features: (t('landing.pricing.plans.basic.features', { returnObjects: true, defaultValue: defaultFeatures.basic }) || defaultFeatures.basic) as string[],
      key: 'basic',
      featured: false
    },
    {
      name: t('landing.pricing.plans.professional.name', 'Professional'),
      price: `15 ${t('landing.pricing.currency', 'KWD')}${t('landing.pricing.per_month', '/mo')}`,
      features: (t('landing.pricing.plans.professional.features', { returnObjects: true, defaultValue: defaultFeatures.professional }) || defaultFeatures.professional) as string[],
      key: 'professional',
      featured: true,
      badge: t('landing.pricing.plans.professional.badge', 'Most Popular')
    },
    {
      name: t('landing.pricing.plans.premium.name', 'Premium'),
      price: `49 ${t('landing.pricing.currency', 'KWD')}${t('landing.pricing.per_month', '/mo')}`,
      features: (t('landing.pricing.plans.premium.features', { returnObjects: true, defaultValue: defaultFeatures.premium }) || defaultFeatures.premium) as string[],
      key: 'premium',
      featured: false
    }
  ];

  return (
    <div className={`landing-page ${isRTL ? 'rtl' : 'ltr'}`}>
      {/* Header */}
      <header className="header">
        <nav className="nav-container">
          <div className="logo">{t('common.appName')}</div>
          <div className="nav-links">
            <a href="#features">{t('navigation.features')}</a>
            <a href="#plans">{t('navigation.pricing')}</a>
            <Link to="/login" className="btn btn-secondary">{t('navigation.clientLogin')}</Link>
            <Link to="/login?type=admin" className="btn btn-primary">{t('navigation.adminLogin')}</Link>
            <LanguageSwitcher />
          </div>
          <div className="mobile-menu-toggle">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1>{t('landing.hero.title')}</h1>
          <p>{t('landing.hero.subtitle')}</p>
          <div className="cta-buttons">
            <button 
              onClick={() => navigate('/signup')} 
              className="btn btn-primary hero-btn"
            >
              {t('landing.hero.cta.primary')}
            </button>
            <a href="#features" className="btn btn-secondary hero-btn">
              {t('landing.hero.cta.secondary')}
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features" id="features">
        <div className="container">
          <h2 className="section-title">{t('landing.features.title')}</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3>{t(feature.titleKey)}</h3>
                <p>{t(feature.descriptionKey)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Plans */}
      <section className="plans" id="plans">
        <div className="container">
          <h2 className="section-title">{t('landing.pricing.title')}</h2>
          <div className="plans-grid">
            {plans.map((plan, index) => (
              <div key={index} className={`plan-card ${plan.featured ? 'featured' : ''}`}>
                {plan.featured && plan.badge && (
                  <div className="featured-badge">{plan.badge}</div>
                )}
                <h3 className="plan-name">{plan.name}</h3>
                <div className="plan-price">{plan.price}</div>
                <ul className="plan-features">
                  {Array.isArray(plan.features) ? plan.features.map((feature, idx) => (
                    <li key={idx}>{feature}</li>
                  )) : (
                    <li>Loading features...</li>
                  )}
                </ul>
                <button 
                  onClick={() => navigate(`/signup?plan=${plan.key}`)} 
                  className="btn btn-primary plan-btn"
                >
                  {t('landing.pricing.cta')}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-links">
          <Link to="/signup">{t('landing.footer.links.signup')}</Link>
          <Link to="/login">{t('landing.footer.links.login')}</Link>
          <Link to="/login?type=admin">{t('landing.footer.links.admin')}</Link>
          <a href="mailto:support@kwtsocial.com">{t('landing.footer.links.support')}</a>
        </div>
        <p>{t('landing.footer.copyright')}</p>
      </footer>
    </div>
  );
};

export default LandingBilingual;