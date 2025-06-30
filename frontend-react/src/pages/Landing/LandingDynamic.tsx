import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTheme } from '../../hooks/useTheme';
import './Landing.css';

const LandingDynamic: React.FC = () => {
  const navigate = useNavigate();
  const { theme, loading } = useTheme();

  // Default features that can be overridden by database
  const defaultFeatures = [
    {
      icon: '🍔',
      title: 'F&B Content Specialist',
      description: 'AI trained specifically for restaurants, cafes, and food businesses in Kuwait'
    },
    {
      icon: '📸',
      title: 'Food Photography Captions',
      description: 'Upload your dish photos and get appetizing descriptions in Arabic & English'
    },
    {
      icon: '🌙',
      title: 'Ramadan & Holiday Specials',
      description: 'Pre-made templates for Iftar, Suhoor, and Kuwait holiday promotions'
    },
    {
      icon: '🏷️',
      title: 'Menu Promotions',
      description: 'Create daily specials, new item launches, and limited-time offers that convert'
    },
    {
      icon: '⭐',
      title: 'Review Response AI',
      description: 'Professional responses to customer reviews in both languages'
    },
    {
      icon: '📊',
      title: 'Peak Hours Insights',
      description: 'Post when hungry customers are browsing - lunch, dinner, and late-night times'
    }
  ];

  // Default plans that can be overridden by database
  const defaultPlans = [
    {
      name: 'Trial',
      price: 'Free',
      features: [
        '7 days free trial',
        '10 AI-generated posts',
        'Basic templates',
        'Email support'
      ],
      buttonText: 'Start Trial',
      featured: false
    },
    {
      name: 'Professional',
      price: `15 ${theme.currency_symbol || 'KWD'}/mo`,
      features: [
        '100 AI-generated posts',
        'Advanced templates',
        'Image enhancement',
        'Priority support',
        'Analytics dashboard'
      ],
      buttonText: 'Get Started',
      featured: true
    },
    {
      name: 'Premium',
      price: `49 ${theme.currency_symbol || 'KWD'}/mo`,
      features: [
        '500 AI-generated posts',
        'Custom templates',
        'Team collaboration',
        'API access',
        'Dedicated support'
      ],
      buttonText: 'Contact Sales',
      featured: false
    }
  ];

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  // Apply dynamic styles
  const heroStyle = theme.hero_style === 'image' && theme.hero_bg_image
    ? { backgroundImage: `url(${theme.hero_bg_image})` }
    : theme.gradient_start && theme.gradient_end
    ? { background: `linear-gradient(135deg, ${theme.gradient_start} 0%, ${theme.gradient_end} 100%)` }
    : {};

  return (
    <div className="landing-page">
      {/* Header */}
      {theme.show_header !== 'false' && (
        <header className="header">
          <nav className="nav-container">
            <div className="logo">
              {theme.logo_url ? (
                <img src={theme.logo_url} alt={theme.site_name || 'Logo'} />
              ) : (
                theme.site_name || 'Kuwait Social AI'
              )}
            </div>
            <div className="nav-links">
              {theme.features_enabled !== 'false' && <a href="#features">Features</a>}
              {theme.pricing_enabled !== 'false' && <a href="#plans">Pricing</a>}
              <Link to="/login" className="btn btn-secondary">Client Login</Link>
              <Link to="/login?type=admin" className="btn btn-primary">Admin Login</Link>
            </div>
            <div className="mobile-menu-toggle">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </nav>
        </header>
      )}

      {/* Hero Section */}
      <section className="hero" style={heroStyle}>
        <div className="container">
          <h1>{theme.hero_title || 'AI-Powered Social Media for Kuwait F&B 🍽️'}</h1>
          <p>{theme.hero_subtitle || 'Create mouth-watering content for restaurants & cafes in Arabic & English instantly'}</p>
          <div className="cta-buttons">
            <button 
              onClick={() => navigate('/signup')} 
              className="btn btn-primary hero-btn"
            >
              {theme.hero_cta_primary || 'Start Free Trial'}
            </button>
            <a href="#features" className="btn btn-secondary hero-btn">
              {theme.hero_cta_secondary || 'Learn More'}
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      {theme.features_enabled !== 'false' && (
        <section className="features" id="features">
          <div className="container">
            <h2 className="section-title">
              {theme.features_title || "Built for Kuwait's Food & Beverage Industry"}
            </h2>
            <div className="features-grid">
              {defaultFeatures.map((feature, index) => (
                <div key={index} className="feature-card">
                  <div className="feature-icon">{feature.icon}</div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Plans */}
      {theme.pricing_enabled !== 'false' && (
        <section className="plans" id="plans">
          <div className="container">
            <h2 className="section-title">
              {theme.pricing_title || 'Simple, Transparent Pricing'}
            </h2>
            <div className="plans-grid">
              {defaultPlans.map((plan, index) => (
                <div key={index} className={`plan-card ${plan.featured ? 'featured' : ''}`}>
                  {plan.featured && <div className="featured-badge">Most Popular</div>}
                  <h3 className="plan-name">{plan.name}</h3>
                  <div className="plan-price">{plan.price}</div>
                  <ul className="plan-features">
                    {plan.features.map((feature, idx) => (
                      <li key={idx}>{feature}</li>
                    ))}
                  </ul>
                  <button 
                    onClick={() => navigate('/signup')} 
                    className="btn btn-primary plan-btn"
                  >
                    {plan.buttonText}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      {theme.show_footer !== 'false' && (
        <footer className="footer">
          <div className="footer-links">
            <Link to="/signup">Sign Up</Link>
            <Link to="/login">Client Login</Link>
            <Link to="/login?type=admin">Admin</Link>
            <a href="mailto:support@kwtsocial.com">Support</a>
          </div>
          <p>&copy; 2024 {theme.site_name || 'Kuwait Social AI'}. Made with ❤️ in Kuwait</p>
        </footer>
      )}
    </div>
  );
};

export default LandingDynamic;