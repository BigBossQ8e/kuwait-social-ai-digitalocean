# SQLAlchemy Relationship Audit for normalized_models.py

## Relationships Found and Required Foreign Keys:

### 1. CompetitorAnalysis (line 15)
- **Relationships:**
  - `top_hashtags` → CompetitorTopHashtag (line 34)
  - `top_posts` → CompetitorTopPost (line 35)
  - `audience_demographics` → CompetitorAudienceDemographic (line 36)
  - `competitor` → Competitor (line 39)

**Required Foreign Keys:**
- CompetitorTopHashtag needs: `analysis_id` FK to `competitor_analysis.id` ✓ (Added)
- CompetitorTopPost needs: `analysis_id` FK to `competitor_analysis.id` ✓ (Added)
- CompetitorAudienceDemographic needs: `analysis_id` FK to `competitor_analysis.id` ✓ (Added)
- CompetitorAnalysis needs: `competitor_id` FK to `competitors.id` (Need to check)

### 2. HashtagStrategy (line 120)
- **Relationships:**
  - `trending_hashtags` → TrendingHashtag (line 139)
  - `recommended_combinations` → HashtagCombination (line 140)
  - `client` → Client (line 143)

**Required Foreign Keys:**
- TrendingHashtag needs: `strategy_id` FK to `hashtag_strategies.id`
- HashtagCombination needs: `strategy_id` FK to `hashtag_strategies.id`
- HashtagStrategy needs: `client_id` FK to `clients.id`

### 3. HashtagCombination (line 182)
- **Relationships:**
  - `hashtags` → HashtagCombinationItem (line 201)
  - `client` → Client (line 200)

**Required Foreign Keys:**
- HashtagCombinationItem needs: `combination_id` FK to `hashtag_combinations.id`
- HashtagCombination needs: `client_id` FK to `clients.id`

### 4. Update Competitor/Client Models (lines 235-237, 247-249)
These appear to be comments/suggestions to add relationships to existing models.

## Foreign Keys to Check/Add: