# Kuwait Social AI - Dynamic Theme System Guide

## Overview

The theme system allows complete rebranding and design customization through the admin portal without any code changes. This is ideal for:
- White-label deployments
- Seasonal themes (Ramadan, National Day)
- A/B testing different designs
- Client-specific branding

## Architecture

### 1. **Database Tables**

```sql
theme_settings      - Individual setting key/value pairs
theme_presets       - Complete theme configurations
theme_history       - Audit trail of all theme changes
```

### 2. **Backend API** (`/api/theme/*`)
- `GET /settings` - Get current theme (public)
- `PUT /settings` - Update theme settings (admin)
- `GET /presets` - List all theme presets
- `POST /presets` - Create new preset
- `POST /presets/:id/activate` - Activate a preset

### 3. **Frontend Integration**
- `useTheme()` hook - Access theme in any component
- CSS variables for dynamic styling
- Real-time preview capabilities

## How It Works

### Dynamic Theme Loading
1. When the app loads, `useTheme()` fetches settings from `/api/theme/settings`
2. Settings are applied as CSS variables to `:root`
3. Components use these variables for styling
4. Changes reflect immediately without refresh

### CSS Variables Applied
```css
--primary-color: #007bff;
--secondary-color: #764ba2;
--gradient-start: #667eea;
--gradient-end: #764ba2;
--text-color: #333;
--bg-color: #ffffff;
--primary-font: system-ui, sans-serif;
--heading-font: inherit;
```

## Admin Features to Implement

### 1. **Theme Editor Component**
```jsx
// Basic structure for admin theme editor
<ThemeEditor>
  <ColorPicker field="primary_color" />
  <ColorPicker field="secondary_color" />
  <GradientPicker fields={['gradient_start', 'gradient_end']} />
  <FontSelector field="primary_font" />
  <TextInput field="hero_title" />
  <ImageUpload field="logo_url" />
  <PreviewPane />
</ThemeEditor>
```

### 2. **Preset Management**
- Save current theme as preset
- Load preset with one click
- Export/import presets
- Set default preset

### 3. **Live Preview**
- Split-screen preview
- Mobile/tablet preview
- Before/after comparison
- Preview link sharing

## Usage Examples

### Change Primary Color
```javascript
const { updateTheme } = useTheme();
await updateTheme({ primary_color: '#ff6b6b' });
```

### Apply Ramadan Theme
```javascript
// Activate a preset
await apiClient.post('/api/theme/presets/3/activate');
```

### Custom CSS Override
```javascript
await updateTheme({
  custom_css: `
    .hero { 
      background-image: url('/ramadan-bg.jpg'); 
    }
    .btn-primary { 
      border-radius: 25px; 
    }
  `
});
```

## Theme Settings Reference

### Branding
- `site_name` - Main site title
- `site_tagline` - Subtitle/tagline
- `logo_url` - Logo image URL
- `favicon_url` - Favicon URL

### Colors
- `primary_color` - Main brand color
- `secondary_color` - Accent color
- `gradient_start` - Hero gradient start
- `gradient_end` - Hero gradient end
- `text_color` - Body text color
- `bg_color` - Background color

### Typography
- `primary_font` - Main font family
- `heading_font` - Headings font
- `font_size_base` - Base font size

### Hero Section
- `hero_title` - Main headline
- `hero_subtitle` - Subheadline
- `hero_cta_primary` - Primary button text
- `hero_cta_secondary` - Secondary button text
- `hero_style` - 'gradient', 'image', or 'video'
- `hero_bg_image` - Background image URL

### Sections
- `features_enabled` - Show/hide features
- `pricing_enabled` - Show/hide pricing
- `show_header` - Show/hide navigation
- `show_footer` - Show/hide footer

### Advanced
- `enable_rtl` - RTL layout for Arabic
- `custom_css` - Custom CSS overrides

## Best Practices

1. **Create Presets for Major Changes**
   - Before making significant changes
   - For seasonal themes
   - For A/B testing

2. **Test on Multiple Devices**
   - Desktop, tablet, mobile
   - Different browsers
   - RTL/LTR layouts

3. **Backup Before Major Changes**
   - Export current theme
   - Save as preset
   - Document in theme history

4. **Performance Considerations**
   - Optimize uploaded images
   - Minimize custom CSS
   - Test loading times

## Deployment Steps

1. **Run Database Migration**
   ```bash
   psql -U postgres -d kuwait_social_ai -f migrations/add_theme_settings.sql
   ```

2. **Update Backend**
   - Add theme models to `__init__.py`
   - Register theme routes in `app_factory.py`

3. **Update Frontend**
   - Replace `Landing` with `LandingDynamic` in App.tsx
   - Ensure CSS uses variables

4. **Create Admin UI**
   - Add theme editor to admin dashboard
   - Add preset management section

## Future Enhancements

1. **Theme Marketplace**
   - Share themes between instances
   - Purchase premium themes
   - Community contributions

2. **AI Theme Generation**
   - Generate color schemes
   - Suggest font pairings
   - Create seasonal themes

3. **Advanced Customization**
   - Component-level theming
   - Animation settings
   - Layout builders

4. **Multi-tenant Theming**
   - Different themes per client
   - Subdomain-based themes
   - User preference themes

## Security Considerations

- Sanitize all user inputs
- Validate image URLs
- Limit custom CSS capabilities
- Audit all theme changes
- Role-based access control

This theme system provides maximum flexibility for rebranding while maintaining code stability and security.