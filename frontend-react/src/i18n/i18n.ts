import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations directly
import enTranslations from './locales/en/translation.json';
import arTranslations from './locales/ar/translation.json';

// Initialize i18n
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslations
      },
      ar: {
        translation: arTranslations
      }
    },
    lng: 'en',
    fallbackLng: 'en',
    debug: false, // Disable debug for production
    
    interpolation: {
      escapeValue: false
    },

    react: {
      useSuspense: false
    }
  });


export default i18n;