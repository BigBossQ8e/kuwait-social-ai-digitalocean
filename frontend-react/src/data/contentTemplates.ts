// Enhanced Content Templates for Kuwait Social AI
// With hyper-localized placeholders and culturally enriched examples

export interface ContentTemplate {
  id: string;
  title: string;
  titleAr: string;
  category: string;
  prompt: string;
  promptAr: string;
  placeholders: {
    [key: string]: {
      example: string;
      exampleAr: string;
      suggestions?: string[];
    };
  };
  hashtags: string[];
}

export const contentTemplates: ContentTemplate[] = [
  // Restaurant & Cafe Templates
  {
    id: 'new-branch-opening',
    title: 'New Branch Opening',
    titleAr: 'افتتاح فرع جديد',
    category: 'restaurant',
    prompt: 'Create an exciting announcement for our new branch opening at {location} on {date}. Highlight {special_features} and mention our {opening_offers}.',
    promptAr: 'اكتب إعلان مشوق عن افتتاح فرعنا الجديد في {location} بتاريخ {date}. اذكر {special_features} والعروض {opening_offers}.',
    placeholders: {
      location: {
        example: 'Salem Al Mubarak St., Salmiya',
        exampleAr: 'شارع سالم المبارك، السالمية',
        suggestions: [
          'The Avenues Mall',
          '360 Mall',
          'Marina Mall',
          'Al Kout Mall',
          'Boulevard, Salmiya',
          'Arabella Complex, Kuwait City',
          'Symphony Mall, Salmiya',
          'Al Hamra Tower',
          'Assima Mall',
          'Gate Mall, Egaila'
        ]
      },
      date: {
        example: 'Thursday, 15th February',
        exampleAr: 'الخميس، ١٥ فبراير',
      },
      special_features: {
        example: 'outdoor seating with sea view, dedicated family section',
        exampleAr: 'جلسة خارجية مع إطلالة بحرية، قسم عائلي مخصص',
      },
      opening_offers: {
        example: '20% discount for first week',
        exampleAr: 'خصم ٢٠٪ للأسبوع الأول',
      }
    },
    hashtags: ['#NewOpening', '#افتتاح_جديد', '#KuwaitRestaurants', '#مطاعم_الكويت']
  },
  
  {
    id: 'dish-promotion',
    title: 'Special Dish Promotion',
    titleAr: 'عرض طبق مميز',
    category: 'restaurant',
    prompt: 'Showcase our {dish_name}, featuring {ingredients}. Available {availability} at {price}. Perfect for {occasion}.',
    promptAr: 'نقدم لكم {dish_name} المحضر من {ingredients}. متوفر {availability} بسعر {price}. مثالي لـ {occasion}.',
    placeholders: {
      dish_name: {
        example: 'Kuwaiti Machboos with Fresh Hammour',
        exampleAr: 'مجبوس كويتي بالهامور الطازج',
        suggestions: [
          'Grilled Zubaidi Fish',
          'Traditional Gabout',
          'Saffron Rice with Shrimps',
          'Lamb Ouzi',
          'Chicken Machboos'
        ]
      },
      ingredients: {
        example: 'local spices, basmati rice, fresh catch from Kuwait waters',
        exampleAr: 'بهارات محلية، رز بسمتي، صيد طازج من مياه الكويت',
      },
      availability: {
        example: 'daily from 12 PM to 10 PM',
        exampleAr: 'يومياً من ١٢ ظهراً حتى ١٠ مساءً',
      },
      price: {
        example: '3.5 KD',
        exampleAr: '٣.٥ د.ك',
      },
      occasion: {
        example: 'family gatherings and special celebrations',
        exampleAr: 'التجمعات العائلية والمناسبات الخاصة',
      }
    },
    hashtags: ['#KuwaitiFoodLovers', '#طعام_كويتي', '#MachboosTime', '#مجبوس']
  },

  {
    id: 'weekend-breakfast',
    title: 'Weekend Breakfast Special',
    titleAr: 'فطور نهاية الأسبوع',
    category: 'restaurant',
    prompt: 'Join us for weekend breakfast at {location}! Try our {special_items} served {timing}. {atmosphere_description}',
    promptAr: 'انضموا لنا لفطور نهاية الأسبوع في {location}! جربوا {special_items} يقدم {timing}. {atmosphere_description}',
    placeholders: {
      location: {
        example: 'our Mishref branch with garden seating',
        exampleAr: 'فرعنا في مشرف مع جلسة حديقة',
      },
      special_items: {
        example: 'traditional Kuwaiti breakfast with rgag bread, cheese, and fresh dates',
        exampleAr: 'فطور كويتي تقليدي مع خبز رقاق، جبن، وتمر طازج',
      },
      timing: {
        example: 'Thursday & Friday 8 AM - 12 PM',
        exampleAr: 'الخميس والجمعة ٨ صباحاً - ١٢ ظهراً',
      },
      atmosphere_description: {
        example: 'Family-friendly atmosphere with kids play area',
        exampleAr: 'أجواء عائلية مع منطقة ألعاب للأطفال',
      }
    },
    hashtags: ['#WeekendBreakfast', '#فطور_نهاية_الأسبوع', '#KuwaitBreakfast', '#ريوق_كويتي']
  },

  // Retail Templates
  {
    id: 'seasonal-sale',
    title: 'Seasonal Sale Announcement',
    titleAr: 'إعلان تخفيضات موسمية',
    category: 'retail',
    prompt: 'Announcing our {season} sale! Get up to {discount}% off on {product_categories}. Visit us at {locations}. Sale ends {end_date}.',
    promptAr: 'نعلن عن تخفيضات {season}! احصل على خصم يصل إلى {discount}٪ على {product_categories}. زورونا في {locations}. ينتهي العرض {end_date}.',
    placeholders: {
      season: {
        example: 'Summer Collection',
        exampleAr: 'مجموعة الصيف',
        suggestions: ['Spring', 'Summer', 'Fall', 'Winter', 'Ramadan', 'Eid', 'National Day']
      },
      discount: {
        example: '70',
        exampleAr: '٧٠',
      },
      product_categories: {
        example: 'all abayas, kaftans, and summer dresses',
        exampleAr: 'جميع العبايات والقفاطين وفساتين الصيف',
      },
      locations: {
        example: 'The Avenues, Marina Mall, and 360 Mall',
        exampleAr: 'الأفنيوز، مارينا مول، و٣٦٠ مول',
      },
      end_date: {
        example: 'February 28th',
        exampleAr: '٢٨ فبراير',
      }
    },
    hashtags: ['#KuwaitSale', '#تخفيضات_الكويت', '#ShoppingKuwait', '#تسوق']
  },

  // Service Business Templates
  {
    id: 'appointment-reminder',
    title: 'Appointment Booking Reminder',
    titleAr: 'تذكير حجز موعد',
    category: 'service',
    prompt: 'Book your {service_type} appointment now! {special_offer} Available slots this week at our {location} branch. Call {phone} or book online.',
    promptAr: 'احجز موعد {service_type} الآن! {special_offer} مواعيد متاحة هذا الأسبوع في فرع {location}. اتصل {phone} أو احجز أونلاين.',
    placeholders: {
      service_type: {
        example: 'spa treatment',
        exampleAr: 'جلسة سبا',
        suggestions: ['haircut', 'dental checkup', 'car service', 'home cleaning']
      },
      special_offer: {
        example: 'Get 15% off on weekday bookings.',
        exampleAr: 'احصل على خصم ١٥٪ للحجوزات في أيام الأسبوع.',
      },
      location: {
        example: 'Jabriya',
        exampleAr: 'الجابرية',
      },
      phone: {
        example: '1234-5678',
        exampleAr: '١٢٣٤-٥٦٧٨',
      }
    },
    hashtags: ['#BookNow', '#احجز_الآن', '#KuwaitServices', '#خدمات_الكويت']
  },

  // Special Events
  {
    id: 'ramadan-iftar',
    title: 'Ramadan Iftar Special',
    titleAr: 'عرض إفطار رمضان',
    category: 'ramadan',
    prompt: 'Join us for iftar at {restaurant_name}! Special Ramadan buffet featuring {menu_highlights} for only {price} per person. {booking_info}',
    promptAr: 'شاركونا الإفطار في {restaurant_name}! بوفيه رمضان الخاص يضم {menu_highlights} بسعر {price} للشخص. {booking_info}',
    placeholders: {
      restaurant_name: {
        example: 'our Al Shaheed Park location',
        exampleAr: 'موقعنا في حديقة الشهيد',
      },
      menu_highlights: {
        example: 'traditional soups, hot & cold mezze, main dishes, and oriental sweets',
        exampleAr: 'شوربات تقليدية، مقبلات باردة وساخنة، أطباق رئيسية، وحلويات شرقية',
      },
      price: {
        example: '12 KD',
        exampleAr: '١٢ د.ك',
      },
      booking_info: {
        example: 'Reserve your table: 1234-5678',
        exampleAr: 'للحجز: ١٢٣٤-٥٦٧٨',
      }
    },
    hashtags: ['#RamadanKuwait', '#رمضان_الكويت', '#IftarTime', '#وقت_الإفطار']
  },

  // Coffee Shop Templates
  {
    id: 'afternoon-coffee',
    title: 'Afternoon Coffee Special',
    titleAr: 'عرض قهوة العصر',
    category: 'cafe',
    prompt: 'Perfect afternoon pick-me-up! Try our {coffee_special} paired with {dessert}. {timing} at all {locations} branches. {ambiance}',
    promptAr: 'قهوة العصر المثالية! جرب {coffee_special} مع {dessert}. {timing} في جميع فروع {locations}. {ambiance}',
    placeholders: {
      coffee_special: {
        example: 'Spanish Latte with saffron',
        exampleAr: 'سبانش لاتيه بالزعفران',
        suggestions: ['Flat White', 'Turkish Coffee', 'Arabic Coffee with dates', 'Iced Karak']
      },
      dessert: {
        example: 'our famous date cake',
        exampleAr: 'كيكة التمر الشهيرة',
      },
      timing: {
        example: 'Daily 3-6 PM',
        exampleAr: 'يومياً ٣-٦ مساءً',
      },
      locations: {
        example: 'Kuwait City and Salmiya',
        exampleAr: 'مدينة الكويت والسالمية',
      },
      ambiance: {
        example: 'Cozy atmosphere perfect for catching up with friends!',
        exampleAr: 'أجواء دافئة مثالية للقاء الأصدقاء!',
      }
    },
    hashtags: ['#AfternoonCoffee', '#قهوة_العصر', '#KuwaitCafe', '#كافيه_الكويت']
  }
];

// Get templates by category
export function getTemplatesByCategory(category: string): ContentTemplate[] {
  return contentTemplates.filter(template => template.category === category);
}

// Get template by ID
export function getTemplateById(id: string): ContentTemplate | undefined {
  return contentTemplates.find(template => template.id === id);
}

// Get all unique categories
export function getTemplateCategories(): string[] {
  return Array.from(new Set(contentTemplates.map(template => template.category)));
}