# Requirements Cleanup Summary

## What Was Done

1. **Created `requirements-dev.txt`** - Moved development-only dependencies:
   - pytest and testing tools
   - black (code formatter)
   - flake8 (linter)
   - tabulate (CLI formatting)

2. **Created `requirements-unused.txt`** - Documented 25 potentially unused packages:
   - Document processing (PyPDF2, python-docx)
   - Language processing (langdetect, arabic-reshaper, python-bidi)
   - Computer vision (opencv-python)
   - Monitoring tools (sentry-sdk, psutil, APScheduler)
   - Telegram integration (python-telegram-bot)
   - Various utilities

3. **Updated `requirements.txt`** - Kept only packages with confirmed imports:
   - Reduced from ~60 packages to ~25 essential packages
   - Kept gunicorn even though not imported (needed for production)
   - Added comments explaining the cleanup

## Packages Removed

The following were moved to `requirements-unused.txt`:
- opencv-python (computer vision - not found in imports)
- langdetect, arabic-reshaper, python-bidi (Arabic language processing)
- PyPDF2, python-docx (document processing)
- python-telegram-bot (Telegram integration placeholder)
- sentry-sdk, psutil, APScheduler (monitoring/scheduling)
- python-json-logger (logging)
- python-dateutil (date utilities)
- gevent (async server)
- python-slugify, validators, phonenumbers (utilities)
- marshmallow-sqlalchemy, cryptography, tinycss2 (might be indirect dependencies)

## Important Notes

1. **Some "unused" packages might actually be needed**:
   - As dependencies of other packages
   - Used dynamically in configuration
   - Required for planned features

2. **Before deploying**:
   - Test thoroughly to ensure nothing breaks
   - Consider keeping Arabic language packages if you plan to support Arabic
   - Keep monitoring tools if you need production monitoring

3. **To install for development**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Recommendations

1. **Test the application** with the cleaned requirements
2. **Add back any packages** that cause import errors
3. **Document why** packages are needed if they're not directly imported
4. **Consider using pip-tools** or similar for better dependency management