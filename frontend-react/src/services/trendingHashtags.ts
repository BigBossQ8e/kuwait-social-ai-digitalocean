// Trending Hashtags Service for Kuwait Social AI
// Provides time-based and context-aware hashtag suggestions

import { format } from 'date-fns';

export interface TrendingHashtag {
  tag: string;
  tagAr: string;
  category: string;
  relevance: number;
  description?: string;
}

export interface TimeBasedHashtags {
  timeOfDay: string;
  hashtags: TrendingHashtag[];
  context: string;
}

// Time-based trending hashtags for Kuwait
const timeBasedTrends: Record<string, TimeBasedHashtags> = {
  earlyMorning: {
    timeOfDay: '5:00 AM - 8:00 AM',
    context: 'Early morning work preparation',
    hashtags: [
      { tag: '#MorningCoffeeKuwait', tagAr: '#قهوة_الصباح', category: 'morning', relevance: 95 },
      { tag: '#KuwaitBreakfast', tagAr: '#ريوق_دوام', category: 'food', relevance: 90 },
      { tag: '#GoodMorningKuwait', tagAr: '#صباح_الخير_الكويت', category: 'greeting', relevance: 85 },
      { tag: '#WorkDayKuwait', tagAr: '#دوام', category: 'work', relevance: 80 },
      { tag: '#TrafficKuwait', tagAr: '#زحمة_الكويت', category: 'traffic', relevance: 75 }
    ]
  },
  
  morning: {
    timeOfDay: '8:00 AM - 12:00 PM',
    context: 'Active work hours',
    hashtags: [
      { tag: '#KuwaitBusiness', tagAr: '#أعمال_الكويت', category: 'business', relevance: 90 },
      { tag: '#CoffeeBreakKW', tagAr: '#استراحة_قهوة', category: 'food', relevance: 85 },
      { tag: '#KuwaitShopping', tagAr: '#تسوق_الكويت', category: 'shopping', relevance: 80 },
      { tag: '#MeetingTime', tagAr: '#وقت_الاجتماعات', category: 'work', relevance: 75 },
      { tag: '#ProductiveKuwait', tagAr: '#إنتاجية', category: 'work', relevance: 70 }
    ]
  },
  
  afternoon: {
    timeOfDay: '12:00 PM - 4:00 PM',
    context: 'Lunch and afternoon activities',
    hashtags: [
      { tag: '#LunchTimeKuwait', tagAr: '#وقت_الغداء', category: 'food', relevance: 95 },
      { tag: '#AfternoonCoffee', tagAr: '#قهوة_العصر', category: 'food', relevance: 90 },
      { tag: '#KuwaitRestaurants', tagAr: '#مطاعم_الكويت', category: 'food', relevance: 85 },
      { tag: '#FamilyLunch', tagAr: '#غداء_عائلي', category: 'family', relevance: 80 },
      { tag: '#AfternoonVibes', tagAr: '#أجواء_العصر', category: 'lifestyle', relevance: 75 }
    ]
  },
  
  evening: {
    timeOfDay: '4:00 PM - 8:00 PM',
    context: 'Post-work and family time',
    hashtags: [
      { tag: '#EveningKuwait', tagAr: '#مساء_الكويت', category: 'greeting', relevance: 90 },
      { tag: '#FamilyTime', tagAr: '#وقت_العائلة', category: 'family', relevance: 85 },
      { tag: '#DinnerTime', tagAr: '#وقت_العشاء', category: 'food', relevance: 80 },
      { tag: '#Zowara', tagAr: '#زوارة', category: 'social', relevance: 95, description: 'Traditional family visit' },
      { tag: '#KuwaitSunset', tagAr: '#غروب_الكويت', category: 'nature', relevance: 75 }
    ]
  },
  
  night: {
    timeOfDay: '8:00 PM - 12:00 AM',
    context: 'Evening social activities',
    hashtags: [
      { tag: '#NightLifeKuwait', tagAr: '#سهرة_كويتية', category: 'entertainment', relevance: 85 },
      { tag: '#DiwaniyaTime', tagAr: '#وقت_الديوانية', category: 'social', relevance: 95 },
      { tag: '#CafeNightKuwait', tagAr: '#كافيه_الليل', category: 'food', relevance: 80 },
      { tag: '#KuwaitDining', tagAr: '#عشاء_الكويت', category: 'food', relevance: 75 },
      { tag: '#FriendsGathering', tagAr: '#جمعة_الربع', category: 'social', relevance: 90 }
    ]
  },
  
  lateNight: {
    timeOfDay: '12:00 AM - 5:00 AM',
    context: 'Late night activities',
    hashtags: [
      { tag: '#LateNightKuwait', tagAr: '#سهرانين', category: 'lifestyle', relevance: 95 },
      { tag: '#MidnightSnack', tagAr: '#وجبة_منتصف_الليل', category: 'food', relevance: 80 },
      { tag: '#NightOwlsKW', tagAr: '#سهرانين_الكويت', category: 'lifestyle', relevance: 85 },
      { tag: '#LateNightDelivery', tagAr: '#توصيل_ليلي', category: 'food', relevance: 75 },
      { tag: '#GamingNightKW', tagAr: '#ليلة_قيمنق', category: 'entertainment', relevance: 70 }
    ]
  }
};

// Day-specific hashtags
const daySpecificTrends: Record<string, TrendingHashtag[]> = {
  friday: [
    { tag: '#FridayPrayers', tagAr: '#صلاة_الجمعة', category: 'religious', relevance: 100 },
    { tag: '#FridayLunch', tagAr: '#غداء_الجمعة', category: 'food', relevance: 95 },
    { tag: '#WeekendVibes', tagAr: '#نهاية_الأسبوع', category: 'lifestyle', relevance: 90 },
    { tag: '#FamilyFriday', tagAr: '#جمعة_العائلة', category: 'family', relevance: 85 }
  ],
  thursday: [
    { tag: '#ThursdayNight', tagAr: '#ليلة_الخميس', category: 'social', relevance: 95 },
    { tag: '#WeekendStartsKW', tagAr: '#بداية_الويكند', category: 'lifestyle', relevance: 90 },
    { tag: '#ThursdayDinner', tagAr: '#عشاء_الخميس', category: 'food', relevance: 85 }
  ]
};

// Seasonal hashtags
const seasonalTrends: Record<string, TrendingHashtag[]> = {
  summer: [
    { tag: '#KuwaitSummer', tagAr: '#صيف_الكويت', category: 'seasonal', relevance: 90 },
    { tag: '#BeatTheHeat', tagAr: '#مكيفات', category: 'lifestyle', relevance: 85 },
    { tag: '#SummerDrinks', tagAr: '#مشروبات_الصيف', category: 'food', relevance: 80 }
  ],
  ramadan: [
    { tag: '#RamadanKuwait', tagAr: '#رمضان_الكويت', category: 'religious', relevance: 100 },
    { tag: '#Iftar', tagAr: '#إفطار', category: 'religious', relevance: 95 },
    { tag: '#Suhoor', tagAr: '#سحور', category: 'religious', relevance: 90 },
    { tag: '#Gergean', tagAr: '#قرقيعان', category: 'cultural', relevance: 85 }
  ]
};

// Location-specific hashtags
const locationHashtags: TrendingHashtag[] = [
  { tag: '#Kuwait360Mall', tagAr: '#٣٦٠_مول', category: 'location', relevance: 85 },
  { tag: '#AvenuesMall', tagAr: '#الأفنيوز', category: 'location', relevance: 90 },
  { tag: '#SalmiyaKuwait', tagAr: '#السالمية', category: 'location', relevance: 80 },
  { tag: '#KuwaitCity', tagAr: '#مدينة_الكويت', category: 'location', relevance: 85 },
  { tag: '#MarinaWalk', tagAr: '#مارينا_ووك', category: 'location', relevance: 75 },
  { tag: '#SalemAlMubarak', tagAr: '#شارع_سالم_المبارك', category: 'location', relevance: 70 }
];

// Get current time period
function getCurrentTimePeriod(): string {
  const hour = new Date().getHours();
  
  if (hour >= 5 && hour < 8) return 'earlyMorning';
  if (hour >= 8 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 16) return 'afternoon';
  if (hour >= 16 && hour < 20) return 'evening';
  if (hour >= 20 && hour < 24) return 'night';
  return 'lateNight';
}

// Get current day of week
function getCurrentDay(): string {
  return format(new Date(), 'EEEE').toLowerCase();
}

// Get current season
function getCurrentSeason(): string {
  const month = new Date().getMonth();
  
  // Check for Ramadan (approximate, would need Hijri calendar API for accuracy)
  const currentYear = new Date().getFullYear();
  // This is a placeholder - in production, use a proper Islamic calendar API
  
  // Summer in Kuwait (May to September)
  if (month >= 4 && month <= 8) return 'summer';
  
  return 'general';
}

// Main function to fetch trending hashtags
export async function fetchTrendingHashtags(
  category?: string,
  includeTimeSpecific: boolean = true,
  includeLocation: boolean = true
): Promise<TrendingHashtag[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  const trendingHashtags: TrendingHashtag[] = [];
  
  // Add time-specific hashtags
  if (includeTimeSpecific) {
    const currentPeriod = getCurrentTimePeriod();
    const timeHashtags = timeBasedTrends[currentPeriod].hashtags;
    trendingHashtags.push(...timeHashtags);
  }
  
  // Add day-specific hashtags
  const currentDay = getCurrentDay();
  if (daySpecificTrends[currentDay]) {
    trendingHashtags.push(...daySpecificTrends[currentDay]);
  }
  
  // Add seasonal hashtags
  const currentSeason = getCurrentSeason();
  if (seasonalTrends[currentSeason]) {
    trendingHashtags.push(...seasonalTrends[currentSeason]);
  }
  
  // Add location hashtags if requested
  if (includeLocation) {
    trendingHashtags.push(...locationHashtags.slice(0, 3)); // Top 3 locations
  }
  
  // Filter by category if specified
  let filteredHashtags = trendingHashtags;
  if (category) {
    filteredHashtags = trendingHashtags.filter(h => h.category === category);
  }
  
  // Sort by relevance and remove duplicates
  const uniqueHashtags = Array.from(
    new Map(filteredHashtags.map(h => [h.tag, h])).values()
  );
  
  return uniqueHashtags
    .sort((a, b) => b.relevance - a.relevance)
    .slice(0, 10); // Return top 10
}

// Get hashtag suggestions for specific business type
export async function getBusinessHashtags(businessType: string): Promise<TrendingHashtag[]> {
  const businessHashtags: Record<string, TrendingHashtag[]> = {
    restaurant: [
      { tag: '#KuwaitFoodie', tagAr: '#عشاق_الأكل_الكويت', category: 'food', relevance: 95 },
      { tag: '#KuwaitRestaurant', tagAr: '#مطعم_الكويت', category: 'business', relevance: 90 },
      { tag: '#FoodDeliveryKW', tagAr: '#توصيل_طعام', category: 'service', relevance: 85 }
    ],
    cafe: [
      { tag: '#KuwaitCoffee', tagAr: '#قهوة_الكويت', category: 'food', relevance: 95 },
      { tag: '#CafeKuwait', tagAr: '#كافيه_الكويت', category: 'business', relevance: 90 },
      { tag: '#SpecialtyCoffee', tagAr: '#قهوة_مختصة', category: 'food', relevance: 85 }
    ],
    retail: [
      { tag: '#ShopKuwait', tagAr: '#تسوق_الكويت', category: 'shopping', relevance: 90 },
      { tag: '#KuwaitFashion', tagAr: '#موضة_الكويت', category: 'fashion', relevance: 85 },
      { tag: '#NewArrivals', tagAr: '#وصل_حديثا', category: 'shopping', relevance: 80 }
    ]
  };
  
  const general = await fetchTrendingHashtags();
  const specific = businessHashtags[businessType] || [];
  
  return [...specific, ...general].slice(0, 15);
}

// Get context for current time
export function getCurrentContext(): TimeBasedHashtags {
  const currentPeriod = getCurrentTimePeriod();
  return timeBasedTrends[currentPeriod];
}