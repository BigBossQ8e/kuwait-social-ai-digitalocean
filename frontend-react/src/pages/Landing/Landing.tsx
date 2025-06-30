import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Landing.css';

const Landing: React.FC = () => {
  const navigate = useNavigate();

  const features = [
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

  const plans = [
    {
      name: 'Basic',
      price: '10 KWD/mo',
      features: [
        '50 AI-generated posts',
        'Basic templates',
        'Email support',
        'Instagram integration'
      ],
      buttonText: 'Contact Sales',
      featured: false
    },
    {
      name: 'Professional',
      price: '15 KWD/mo',
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
      price: '49 KWD/mo',
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

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="header">
        <nav className="nav-container">
          <div className="logo">Kuwait Social AI</div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#plans">Pricing</a>
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

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1>AI-Powered Social Media for Kuwait F&B 🍽️</h1>
          <p>Create mouth-watering content for restaurants & cafes in Arabic & English instantly</p>
          <div className="cta-buttons">
            <button 
              onClick={() => navigate('/signup')} 
              className="btn btn-primary hero-btn"
            >
              Get Started
            </button>
            <a href="#features" className="btn btn-secondary hero-btn">Learn More</a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features" id="features">
        <div className="container">
          <h2 className="section-title">Built for Kuwait's Food & Beverage Industry</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Plans */}
      <section className="plans" id="plans">
        <div className="container">
          <h2 className="section-title">Simple, Transparent Pricing</h2>
          <div className="plans-grid">
            {plans.map((plan, index) => (
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
                  onClick={() => navigate(`/signup?plan=${plan.name.toLowerCase()}`)} 
                  className="btn btn-primary plan-btn"
                >
                  Get Started
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-links">
          <Link to="/signup">Sign Up</Link>
          <Link to="/login">Client Login</Link>
          <Link to="/login?type=admin">Admin</Link>
          <a href="mailto:support@kwtsocial.com">Support</a>
        </div>
        <p>&copy; 2024 Kuwait Social AI. Made with ❤️ in Kuwait</p>
      </footer>
    </div>
  );
};

export default Landing;