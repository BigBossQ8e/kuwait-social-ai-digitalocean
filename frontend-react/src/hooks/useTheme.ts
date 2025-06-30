import { useState, useEffect } from 'react';
import { apiClient } from '../services/api/apiClient';

interface ThemeSettings {
  // Branding
  site_name?: string;
  site_tagline?: string;
  logo_url?: string;
  favicon_url?: string;
  
  // Colors
  primary_color?: string;
  secondary_color?: string;
  gradient_start?: string;
  gradient_end?: string;
  text_color?: string;
  bg_color?: string;
  
  // Typography
  primary_font?: string;
  heading_font?: string;
  font_size_base?: string;
  
  // Hero Section
  hero_title?: string;
  hero_subtitle?: string;
  hero_cta_primary?: string;
  hero_cta_secondary?: string;
  hero_style?: 'gradient' | 'image' | 'video';
  hero_bg_image?: string;
  
  // Features
  features_enabled?: string;
  features_title?: string;
  
  // Pricing
  pricing_enabled?: string;
  pricing_title?: string;
  currency_symbol?: string;
  
  // Layout
  show_header?: string;
  show_footer?: string;
  enable_rtl?: string;
  
  // Custom CSS
  custom_css?: string;
}

export const useTheme = () => {
  const [theme, setTheme] = useState<ThemeSettings>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchThemeSettings();
  }, []);

  const fetchThemeSettings = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/theme/settings');
      setTheme(response.data.settings);
      applyThemeSettings(response.data.settings);
    } catch (err) {
      console.error('Failed to load theme settings:', err);
      setError('Failed to load theme settings');
      // Use default theme on error
      setTheme(getDefaultTheme());
    } finally {
      setLoading(false);
    }
  };

  const applyThemeSettings = (settings: ThemeSettings) => {
    const root = document.documentElement;
    
    // Apply CSS variables
    if (settings.primary_color) {
      root.style.setProperty('--primary-color', settings.primary_color);
    }
    if (settings.secondary_color) {
      root.style.setProperty('--secondary-color', settings.secondary_color);
    }
    if (settings.gradient_start) {
      root.style.setProperty('--gradient-start', settings.gradient_start);
    }
    if (settings.gradient_end) {
      root.style.setProperty('--gradient-end', settings.gradient_end);
    }
    if (settings.text_color) {
      root.style.setProperty('--text-color', settings.text_color);
    }
    if (settings.bg_color) {
      root.style.setProperty('--bg-color', settings.bg_color);
    }
    
    // Apply fonts
    if (settings.primary_font) {
      root.style.setProperty('--primary-font', settings.primary_font);
    }
    if (settings.heading_font) {
      root.style.setProperty('--heading-font', settings.heading_font);
    }
    if (settings.font_size_base) {
      root.style.setProperty('--font-size-base', settings.font_size_base);
    }
    
    // Apply favicon
    if (settings.favicon_url) {
      const favicon = document.querySelector("link[rel*='icon']") as HTMLLinkElement;
      if (favicon) {
        favicon.href = settings.favicon_url;
      }
    }
    
    // Apply custom CSS
    if (settings.custom_css) {
      let styleElement = document.getElementById('theme-custom-css');
      if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'theme-custom-css';
        document.head.appendChild(styleElement);
      }
      styleElement.textContent = settings.custom_css;
    }
    
    // Update document title
    if (settings.site_name) {
      document.title = settings.site_name;
    }
  };

  const getDefaultTheme = (): ThemeSettings => {
    return {
      site_name: 'Kuwait Social AI',
      site_tagline: 'AI-Powered Social Media for Kuwait F&B',
      primary_color: '#007bff',
      secondary_color: '#764ba2',
      gradient_start: '#667eea',
      gradient_end: '#764ba2',
      text_color: '#333333',
      bg_color: '#ffffff',
      hero_title: 'AI-Powered Social Media for Kuwait F&B 🍽️',
      hero_subtitle: 'Create mouth-watering content for restaurants & cafes in Arabic & English instantly',
      hero_cta_primary: 'Start Free Trial',
      hero_cta_secondary: 'Learn More',
      features_enabled: 'true',
      pricing_enabled: 'true'
    };
  };

  const updateTheme = async (newSettings: Partial<ThemeSettings>) => {
    try {
      const response = await apiClient.put('/api/theme/settings', {
        settings: newSettings
      });
      
      if (response.data.success) {
        const updatedTheme = { ...theme, ...newSettings };
        setTheme(updatedTheme);
        applyThemeSettings(updatedTheme);
        return true;
      }
      return false;
    } catch (err) {
      console.error('Failed to update theme:', err);
      return false;
    }
  };

  return {
    theme,
    loading,
    error,
    updateTheme,
    refreshTheme: fetchThemeSettings
  };
};