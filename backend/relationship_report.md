# SQLAlchemy Relationship Analysis Report

## Summary
Based on the audit report and our analysis, we need to fix the following relationships:

## Required Fixes

### 1. User Model
Current relationships:
- `owner_profile` -> Owner (back_populates="user")
- `admin_profile` -> Admin (back_populates="user") 
- `client_profile` -> Client (back_populates="user")

**Status**: ✅ Correct on User side

### 2. Owner Model  
Needs:
- `user` -> User (back_populates="owner_profile")

**Status**: ❌ Has wrong back_populates value

### 3. Admin Model
Needs:
- `user` -> User (back_populates="admin_profile")

**Status**: ❌ Missing relationship

### 4. Client Model
Needs:
- `user` -> User (back_populates="client_profile")

**Status**: ❌ Missing relationship

### 5. Post Model
Needs:
- `client` -> Client (back_populates="posts")
- `analytics` -> PostAnalytics (back_populates="post")

**Status**: ❌ Missing both relationships

### 6. SocialAccount Model
Needs:
- `posts` -> Post (back_populates="social_account")

**Status**: ❌ Missing relationship

### 7. Analytics Model
Needs:
- `client` -> Client (back_populates="analytics")

**Status**: ❌ Missing relationship

### 8. PostAnalytics Model
Already has:
- `post` -> Post (back_populates="analytics")

**Status**: ✅ Correct

## Action Plan

1. **Manual Fix Required**: Since the automated script isn't working perfectly, we should manually add these relationships to the models.py file on the server.

2. **Deploy the Fixed models.py**: Copy the corrected file to the server.

3. **Test**: Restart the backend and verify all relationships work.

## Code to Add

```python
# In Admin class:
user = db.relationship("User", back_populates="admin_profile")

# In Client class:  
user = db.relationship("User", back_populates="client_profile")

# In Owner class (fix existing):
# Change from: user = db.relationship("User", back_populates="admin_profile")
# To: user = db.relationship("User", back_populates="owner_profile")

# In Post class:
client = db.relationship("Client", back_populates="posts")
analytics = db.relationship("PostAnalytics", back_populates="post", uselist=False)

# In SocialAccount class:
posts = db.relationship("Post", back_populates="social_account")

# In Analytics class:
client = db.relationship("Client", back_populates="analytics")
```