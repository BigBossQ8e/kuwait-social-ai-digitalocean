# Kuwait Social AI - Admin-Controlled Signup Flow

## Overview

The signup process is designed to give admins full control over who gets access and what type of access they receive. There is NO automatic free trial - trials are gifted by admins.

## Client Signup Flow

### 1. **Client Registration**
- Client fills out signup form at `/signup`
- Required information:
  - Company name
  - Contact name
  - Email
  - Kuwait phone number
  - Password

### 2. **Account Created (Inactive)**
- Account is created but **NOT active**
- Status: `pending_approval`
- Client sees: "Your account is pending approval. We will contact you soon."
- Client CANNOT login yet

### 3. **Admin Review**
- Admin receives notification of new signup
- Admin reviews client information
- Admin can see all pending clients at `/admin/pending-clients`

### 4. **Admin Approval Options**

#### Option A: Approve with Gift Trial
```json
{
  "gift_trial_days": 7,  // Admin decides trial length
  "subscription_plan": "trial"
}
```
- Client gets X days free trial
- After trial ends, client must pay

#### Option B: Approve without Trial
```json
{
  "gift_trial_days": 0,
  "subscription_plan": "basic"  // or "professional", "premium"
}
```
- Client account activated
- Status: `pending_payment`
- Client must pay before using platform

#### Option C: Reject
- Admin can reject suspicious or unwanted signups
- Client account remains inactive

### 5. **Client Notification**
- Client receives email about approval status
- If approved with trial: "Welcome! You have been gifted a 7-day trial"
- If approved without trial: "Welcome! Please complete payment to activate"

## Database Changes

### User Table
```sql
is_active: FALSE  -- Default for new signups
```

### Client Table
```sql
subscription_status: 'pending_approval'  -- New default
subscription_plan: 'pending'  -- Not 'trial'
subscription_start: NULL  -- No dates until approved
subscription_end: NULL
```

## API Endpoints

### 1. **POST /api/auth/register**
- Creates inactive account
- No trial assignment
- Returns pending status

### 2. **GET /api/admin/pending-clients**
- Lists all clients awaiting approval
- Admin/Owner only

### 3. **POST /api/admin/approve-client/:id**
- Approves or rejects client
- Sets trial days (if any)
- Admin/Owner only

## Benefits of This Approach

1. **Quality Control**: Admin reviews every signup
2. **Flexible Trials**: Different trial lengths for different clients
3. **No Abuse**: Prevents trial abuse with fake accounts
4. **Personal Touch**: Can call/email client before approval
5. **Revenue Protection**: Most clients start with paid plans

## Admin Dashboard Features Needed

### Pending Approvals Widget
```jsx
<PendingApprovals>
  - New signups count
  - List with client details
  - Quick approve/reject buttons
  - Gift trial days selector
</PendingApprovals>
```

### Approval Form
```jsx
<ApprovalForm>
  - Client information display
  - Trial days input (0-30)
  - Plan selection
  - Approval notes
  - Send welcome email checkbox
</ApprovalForm>
```

## Email Templates Needed

1. **Registration Received**
   - "Thank you for registering. Your account is under review."

2. **Account Approved (With Trial)**
   - "Welcome! You've been gifted a [X]-day trial."

3. **Account Approved (No Trial)**
   - "Welcome! Please complete payment to activate your account."

4. **Account Rejected**
   - "Unfortunately, we cannot approve your account at this time."

## Implementation Priority

1. ✅ Update landing page (remove free trial mentions)
2. ✅ Update registration endpoint (no auto-trial)
3. ⏳ Create admin approval interface
4. ⏳ Add pending clients list to admin dashboard
5. ⏳ Implement email notifications
6. ⏳ Add payment flow for non-trial approvals

This approach ensures that every client is vetted and trials are used strategically rather than given away automatically.