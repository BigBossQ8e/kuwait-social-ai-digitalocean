import React from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageSwitcher.css';

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'ar' : 'en';
    i18n.changeLanguage(newLang);
    
    // Update document direction for RTL/LTR
    document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLang;
    
    // Store preference
    localStorage.setItem('preferredLanguage', newLang);
  };

  return (
    <button 
      className="language-switcher"
      onClick={toggleLanguage}
      aria-label="Switch language"
    >
      {i18n.language === 'en' ? (
        <>
          <span className="lang-text">العربية</span>
          <span className="lang-flag">🇰🇼</span>
        </>
      ) : (
        <>
          <span className="lang-text">English</span>
          <span className="lang-flag">🇬🇧</span>
        </>
      )}
    </button>
  );
};

export default LanguageSwitcher;