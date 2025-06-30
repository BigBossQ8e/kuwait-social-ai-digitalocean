# Kuwait Compliance Requirements for Kuwait Social AI

## 🇰🇼 Essential Compliance Features

### 1. **Mobile Phone Verification (OTP)**
- **Required**: All Kuwait businesses must verify mobile numbers
- **Format**: Kuwait numbers (+965 XXXX XXXX)
- **Implementation**: SMS OTP verification before account activation

### 2. **Kuwait Phone Number Validation**
- Must start with +965
- Valid prefixes: 5, 6, 9 (mobile), 2 (landline)
- Length: 8 digits after country code

### 3. **Business Registration**
- **Commercial License Number**: Required for businesses
- **Civil ID**: Required for individuals
- **PACI Number**: For address verification

### 4. **Content Compliance**
- No alcohol-related content
- No gambling references
- No dating/adult content
- Respect for Islamic values
- No political content without approval

### 5. **Language Requirements**
- Arabic language support mandatory
- Bilingual content (Arabic/English)
- RTL (Right-to-Left) support for Arabic

### 6. **Data Residency**
- Sensitive data should be stored within GCC region
- Payment data must comply with Kuwait Central Bank regulations

### 7. **Prayer Times Integration**
- Respect for prayer times in scheduling
- No promotional messages during prayer times
- Friday prayer considerations (12:00-13:30)

### 8. **Local Holidays & Events**
- Kuwait National Day (Feb 25)
- Liberation Day (Feb 26)
- Ramadan considerations
- Eid holidays

### 9. **Payment Methods**
- KNET integration (Kuwait's payment gateway)
- Local bank support
- Invoice generation in KWD

### 10. **Privacy & Data Protection**
- Comply with Kuwait's Data Privacy Protection Regulation
- User consent for data collection
- Right to data deletion

## Implementation Priority:

### Phase 1 (Immediate):
1. ✅ Phone number validation for +965
2. ⏳ SMS OTP verification
3. ⏳ Arabic language in critical areas
4. ✅ Content filtering

### Phase 2 (Next Sprint):
1. Commercial license field
2. KNET payment integration
3. Full Arabic translation
4. Prayer times API integration

### Phase 3 (Future):
1. PACI address verification
2. Advanced content moderation
3. Local hosting option
4. Central Bank compliance for payments

## Technical Implementation Needed:

### 1. SMS OTP Service
- Twilio/Vonage with Kuwait support
- Local SMS gateway (Ooredoo/Zain/STC)

### 2. Validation Rules
```javascript
// Kuwait phone validation
const isValidKuwaitPhone = (phone) => {
  const kuwaitRegex = /^\+965[569]\d{7}$/;
  return kuwaitRegex.test(phone);
};

// Business license format
const isValidCommercialLicense = (license) => {
  // Format: XXXXX/YYYY (5 digits / 4 digit year)
  const licenseRegex = /^\d{5}\/\d{4}$/;
  return licenseRegex.test(license);
};
```

### 3. Content Filtering Keywords
- Alcohol (كحول, خمر, مشروبات كحولية)
- Gambling (قمار, مراهنات)
- Dating (مواعدة, تعارف)
- Political parties/figures

### 4. Prayer Times Scheduling
- No posts during:
  - Fajr
  - Dhuhr (especially Friday)
  - Asr
  - Maghrib
  - Isha

## Compliance Checklist for Admin Panel:

- [ ] Add Commercial License field to client registration
- [ ] Implement Kuwait phone number validation
- [ ] Add SMS OTP verification
- [ ] Add content compliance warnings
- [ ] Add Arabic labels for key fields
- [ ] Implement prayer time scheduling restrictions
- [ ] Add KNET payment option
- [ ] Add data privacy consent checkbox

## Resources:
- Kuwait Central Bank: https://www.cbk.gov.kw
- PACI (Public Authority for Civil Information): https://www.paci.gov.kw
- Kuwait Prayer Times API: https://aladhan.com/prayer-times-api