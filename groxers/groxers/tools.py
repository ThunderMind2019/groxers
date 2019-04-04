
def cleanse(list_or_str):
    if isinstance(list_or_str, str):
        return list_or_str.strip()
    
    return [s.strip() for s in list_or_str if s.strip()]

def get_main_category(sub_cat):
    for cat, k_words in main_to_sub_category_map.items():
        for key in k_words:
            if key in sub_cat or sub_cat in key:
                return cat

def get_sub_category(category_strs):
    for category, keywords in sub_category_map.items():
        for keyword in sorted(keywords, key=len, reverse=True):
            if keyword in category_strs:
                return category

sub_category_map = {
    'bags': ['bags', 'clutch', 'luggage'],
    'shawls/stoles': ['shawls', 'stoles'],
    'bottoms': ['shalwar', 'bottoms', 'trousers', 'pants', 'denim', 'tights'],
    'footwear': ['footwear', 'shoes', 'sandals', 'boots'],
    'stitched': ['stitched', 'embroidered', 'pret', 'suits'],
    'unstitched': ['unstitched', 'fabric', 'latha'],
    'stitched/unstitched': ['collection', 'summer', 'fall', 'winter', 'spring'],
    'tops': ['kurti', 'shirt', 'kurta', 'tops', 'sweaters', 'coat'],
    'dresses': ['dress', 'piece suit', 'piece dress'],
    'socks': ['socks'],
    'undergarments': ['undergarments', 'underwear', 'under wear', 'boxers', 'vest',],
    'hair accessories': ['hair accessories'],
    'juicer blender & grinder': ['juicer', 'blender', 'grinder'],
    'irons': ['irons',],
    'shavers & trimmers': ['shavers & trimmers',],
    'kettles & coffee makers': ['kettles', 'coffee makers',],
    'vacuum cleaners': ['vacuum cleaners',],
    'fryers': ['fryers',],
    'fans': ['fans',],
    'e mixer': ['e mixer',],
    'toaster & sandwich maker': ['toaster','sandwich maker',],
    'medical accessories': ['medical accessories',],
    'kitchen items': ['kitchen items',],
    'scales': ['scales',],
    'humidifier': ['humidifier',],
    'choppers': ['choppers',],
    'emergency lights': ['emergency lights',],
    'bbq grills': ['bbq grills',],
    'tissue box': ['tissue box',],
    'bowls': ['bowls',],
    'ashtray': ['ashtray',],
    'trays': ['trays',],
    'candle stands': ['candle stands',],
    'mirrors': ['face mirrors',],
    'bath decor': ['bath decor',],
    'flowers': ['flowers',],
    'vase': ['vase',],
    'mix decoration items': ['mix decoration items',],
    'photo frame & album decor': ['photo frame', 'album decor',],
    'jewellery box': ['jewellery box'],
    'dog food': ['dog food',],
    'cat food': ['cat food'],
    'feed': ['animal feed', 'pet food'],
    'insecticides': ['insecticides',],
    'kitchen ware': ['kitchen ware',],
    'laundry': ['laundry',],
    'cleaners': ['cleaners',],
    'electric goods': ['electric goods',],
    'plastic & paper goods': ['plastic & paper goods',],
    'home goods': ['home goods',],
    'car care': ['car care',],
    'toiletries': ['toiletries', 'soap', 'detergents'],
    'hair care': ['hair care',],
    'personal care': ['personal care',],
    'skin care': ['skin care',],
    'cosmetic': ['cosmetic',],
    'perfume': ['perfume',],
    'dairy': ['dairy',],
    'pantry': ['pantry',],
    'beverages': ['beverages', 'coffee', 'tea', 'soft drink'],
    'frozen food': ['frozen food',],
    'deli': ['deli',],
    'general items': ['noodles', 'pasta', 'sauce', 'ghee', 'oil', 'olives', 'bakery',
                      'biscuits', 'cereal', 'pulses', 'rice', 'atta', 'spices'],
    'snacks': ['snack', 'confectionary'],
    'home baking': ['baking',],
    'diet and nutrition': ['diet', 'nutrition',],
    'fruits & vegetables': ['fruits', 'vegetables',],
    'video games': ['video games'],
    'educational toys': ['educational toys'],
    'activity toys': ['girls toys', 'boys toys', 'packed vehicles', 'toys'],
    'baby products': ['baby products', 'baby items'],
    'baby feeding': ['baby feeding'],
    'diapers': ['diapers'],
    'other electronics': ['insect killers', 'electric', 'electronics'],
    'other accessories': ['accessories'],
    'mens': ['men', 'boys'],
    'girls': ['girls'],
}

main_to_sub_category_map = {
    'Electronics': ['hair accessories', 'juicer blender & grinder', 'irons', 'shavers & trimmers',
                    'kettles & coffee makers', 'vacuum cleaners', 'fryers', 'fans', 'e mixer',
                    'toaster & sandwich maker', 'insect killers', 'medical accessories',
                    'scales', 'humidifier', 'choppers', 'emergency lights', 'bbq grills', 'other electronics'],
    "Men's Clothing": ['mens'],
    "Women's Clothing": ['unstitched', 'stitched', 'bottoms', 'girls', 'tops', 'dresses'],
    'Accessories': ['bags', 'shawls/stoles', 'socks', 'undergarments', 'other accessories'],
    'Decoration': ['tissue box', 'bowls', 'ashtray', 'trays', 'candle stands',
                   'mirrors', 'bath decor', 'flowers', 'vase', 'mix decoration items',
                   'photo frame & album decor', 'jewellery box'],
    'Toys': ['video games', 'educational toys', 'activity toys'] ,
    'Grocery': ['dairy', 'pantry', 'beverages', 'frozen food', 'deli', 'general items'
                'snacks', 'home baking', 'diet and nutrition', 'fruits & vegetables'],
    'Health and Beauty': ['toiletries', 'hair care', 'personal care', 'skin care', 'cosmetic', 'perfume'],
    'Household Essentials': ['insecticides', 'kitchen ware', 'laundry', 'cleaners', 'kitchen items',
                             'electric goods', 'plastic & paper goods', 'home goods', 'car care'],
    'Baby Care': ['baby products', 'baby feeding', 'diapers'],
    'Pet Food': ['dog food', 'feed', 'cat food',],
}
