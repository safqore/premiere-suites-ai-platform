#!/usr/bin/env python3
"""
Map FAQ IDs to their correct sections based on the actual FAQ page structure
"""

# Based on the actual FAQ page structure, here's the mapping:
FAQ_SECTION_MAPPING = {
    # About Us section (fq_1 to fq_3)
    "FQ_1": "About Us",    # Why choose Premiere Suites?
    "FQ_2": "About Us",    # How are your short-term and long-term rental rates determined?
    "FQ_3": "About Us",    # What is Premiere Suites Alliance?
    
    # Reservations section (fq_4 to fq_12)
    "FQ_4": "Reservations",    # How do I book a reservation
    "FQ_5": "Reservations",    # Can I book my stay online?
    "FQ_6": "Reservations",    # What is the minimum stay requirement?
    "FQ_7": "Reservations",    # Can I extend my stay?
    "FQ_8": "Reservations",    # Do you take advanced reservations?
    "FQ_9": "Reservations",    # Can I receive a lower rate if I stay longer?
    "FQ_10": "Reservations",   # Do you offer large group rentals?
    "FQ_11": "Reservations",   # What are the check-in/check-out times?
    "FQ_12": "Reservations",   # Can I cancel my reservation?
    
    # Payment section (fq_13 to fq_16)
    "FQ_13": "Payment",        # What method of payment do you accept?
    "FQ_14": "Payment",        # Do you require a security deposit?
    "FQ_15": "Payment",        # When will I be charged for my reservation?
    "FQ_16": "Payment",        # Are there any hidden fees?
    
    # Guest Services section (fq_17 to fq_27)
    "FQ_17": "Guest Services", # What is included in a furnished apartment?
    "FQ_18": "Guest Services", # Do you offer a convenience item starter kit?
    "FQ_19": "Guest Services", # How do I pick up/drop off the keys to my unit?
    "FQ_20": "Guest Services", # Do you offer housekeeping?
    "FQ_21": "Guest Services", # Do you offer rentals with parking?
    "FQ_22": "Guest Services", # Can I use the building amenities?
    "FQ_23": "Guest Services", # Can I make international phone calls?
    "FQ_24": "Guest Services", # Can I order extra television channels and movies?
    "FQ_25": "Guest Services", # How do I log into the WI-FI?
    "FQ_26": "Guest Services", # Do you offer storage units during my stay?
    "FQ_27": "Guest Services", # Do your properties have bike racks or electric car changing?
    
    # Rules and Regulations section (fq_28 to fq_30)
    "FQ_28": "Rules and Regulations", # Is smoking allowed in rental units?
    "FQ_29": "Rules and Regulations", # Do you offer pet-friendly rentals?
    "FQ_30": "Rules and Regulations", # What are your terms and conditions?
}

def get_section_for_faq(faq_id):
    """Get the correct section for a given FAQ ID"""
    return FAQ_SECTION_MAPPING.get(faq_id, "General")

def update_faq_categories():
    """Update the FAQ data file with correct section names"""
    import json
    
    # Read the current FAQ data
    with open('premiere_suites_faq_data.jsonl', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process each line
    updated_lines = []
    for line in lines:
        try:
            data = json.loads(line.strip())
            
            # Update FAQ entries with correct sections
            if data.get('type') == 'faq':
                faq_id = data.get('id')
                if faq_id in FAQ_SECTION_MAPPING:
                    data['category'] = FAQ_SECTION_MAPPING[faq_id]
                    # Also update the text_chunk
                    if 'text_chunk' in data:
                        # Update the category in the text chunk
                        text_parts = data['text_chunk'].split(' | ')
                        for i, part in enumerate(text_parts):
                            if part.startswith('Category:'):
                                text_parts[i] = f"Category: {FAQ_SECTION_MAPPING[faq_id]}"
                                break
                        data['text_chunk'] = ' | '.join(text_parts)
            
            # Update summary with new categories
            elif data.get('type') == 'summary':
                data['categories'] = list(set(FAQ_SECTION_MAPPING.values()))
                data['categories_covered'] = len(data['categories'])
            
            updated_lines.append(json.dumps(data, ensure_ascii=False))
            
        except json.JSONDecodeError:
            # Keep non-JSON lines as is (like metadata)
            updated_lines.append(line.strip())
    
    # Write back the updated data
    with open('premiere_suites_faq_data.jsonl', 'w', encoding='utf-8') as f:
        for line in updated_lines:
            f.write(line + '\n')
    
    print("FAQ categories updated successfully!")
    print(f"New sections: {list(set(FAQ_SECTION_MAPPING.values()))}")

if __name__ == "__main__":
    update_faq_categories()
