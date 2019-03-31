
def cleanse(list_or_str):
    if isinstance(list_or_str, str):
        return list_or_str.strip()
    
    return [s.strip() for s in list_or_str if s]


category_map = {
    'Shoes': ['footwear', 'shoes', 'sandals', 'boots'],
    'Dresses': ['stitched', 'unstitched', 'pret'],
    'Shirts': ['kurti'],
    'Accessories': ['accessories', 'bags'],
}