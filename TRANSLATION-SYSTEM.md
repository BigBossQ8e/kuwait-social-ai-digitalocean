# Translation System Documentation

## Overview

Kuwait Social AI now features a comprehensive database-backed translation system that allows dynamic management of translations without requiring code deployment.

## Features

- **Database-Backed Storage**: All translations stored in PostgreSQL
- **Admin Panel Editor**: Visual interface for managing translations
- **API Endpoints**: RESTful API for CRUD operations
- **Caching**: 5-minute cache for performance
- **Version History**: Track all translation changes
- **Import/Export**: JSON format for bulk operations
- **Bilingual Support**: English and Arabic with RTL
- **Real-time Updates**: Changes reflect immediately

## Architecture

### Database Schema

```sql
-- Main translations table
translations
  - id (primary key)
  - key (string) - e.g., "landing.hero.title"
  - locale (string) - "en" or "ar"
  - value (text) - The translated text
  - category (string) - For grouping
  - created_at, updated_at
  - created_by (foreign key to users)

-- History tracking
translation_history
  - id (primary key)
  - translation_id (foreign key)
  - old_value, new_value
  - changed_by (foreign key to users)
  - changed_at
```

### API Endpoints

- `GET /api/translations` - Get all translations for a locale
- `GET /api/translations/list` - Get translations in list format (admin)
- `POST /api/translations` - Create new translation
- `PUT /api/translations/:id` - Update translation
- `PUT /api/translations/bulk` - Bulk update translations
- `DELETE /api/translations/:id` - Delete translation
- `GET /api/translations/export` - Export all as JSON
- `POST /api/translations/import` - Import from JSON
- `GET /api/translations/history/:id` - Get change history

### Frontend Integration

The frontend uses a custom i18next backend that:
1. Fetches translations from API on load
2. Caches for 5 minutes
3. Falls back to static files if API fails
4. Updates cache after admin edits

## Setup Instructions

### 1. Run Database Migration

```bash
cd backend
psql -U postgres -d kuwait_social_ai -f migrations/add_translations_tables.sql
```

### 2. Populate Initial Translations

```bash
cd backend
python scripts/populate_translations.py
```

### 3. Enable API Backend (Optional for Development)

```bash
# In frontend/.env
REACT_APP_USE_API_TRANSLATIONS=true
```

## Admin Usage

### Accessing Translation Editor

1. Login as admin
2. Navigate to Admin Dashboard
3. Click "Translations" tab

### Features

- **Search**: Find translations by key or text
- **Filter**: By category or missing translations
- **Edit**: Click edit icon, modify, save
- **Export**: Download all translations as JSON
- **Missing**: Toggle to see untranslated items

### Best Practices

1. **Use Descriptive Keys**: `landing.hero.title` not `title1`
2. **Group by Feature**: Keep related translations together
3. **Test RTL**: Always verify Arabic text direction
4. **Preserve Placeholders**: Keep {{variables}} intact
5. **Review Changes**: Check history before major updates

## Development Workflow

### Adding New Translations

1. Add to local JSON files first
2. Run populate script to sync to database
3. Or add directly via admin panel

### Translation Keys Format

```
category.section.item.property
```

Examples:
- `landing.hero.title`
- `auth.login.submit`
- `dashboard.stats.totalPosts`

### Using Translations in Code

```typescript
import { useTranslation } from 'react-i18next';

const Component = () => {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('landing.hero.title')}</h1>
      <p>{t('dashboard.welcome', { name: userName })}</p>
    </div>
  );
};
```

## Deployment

### Production Setup

1. Ensure database migrations are run
2. Set `NODE_ENV=production` for API backend
3. Run populate script for initial data
4. Grant admin users translation permissions

### Performance Considerations

- Translations cached for 5 minutes
- API only called on language change
- Static files as emergency fallback
- Consider CDN for static translations

## Troubleshooting

### Translations Not Updating

1. Clear browser localStorage
2. Check API endpoint is accessible
3. Verify cache has expired (5 min)
4. Check browser console for errors

### Missing Translations

1. Check key exists in database
2. Verify locale is correct
3. Use admin panel "Missing" filter
4. Check fallback language

### RTL Issues

1. Ensure Arabic locale is active
2. Check CSS direction properties
3. Verify component RTL support
4. Test with Arabic system locale

## Future Enhancements

- [ ] Translation approval workflow
- [ ] Machine translation integration
- [ ] Translation memory/suggestions
- [ ] Pluralization rules
- [ ] Context screenshots
- [ ] Translation analytics
- [ ] A/B testing for translations
- [ ] Webhook notifications