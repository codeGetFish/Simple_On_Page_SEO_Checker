import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import Counter
from urllib.parse import urljoin

def get_seo_information(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    base_url = response.url

    # Get the page title
    title = soup.title.text.strip()

    # Get the meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        meta_description = meta_description['content'].strip()
    else:
        meta_description = 'N/A'

    # Get heading tags with levels
    headings = []
    for heading_level in range(1, 7):
        heading_tags = soup.find_all(f'h{heading_level}')
        for heading_tag in heading_tags:
            headings.append({'level': heading_level, 'text': heading_tag.text.strip()})

    # Get image links with alt text
    image_links_with_alt_text = []
    image_tags = soup.find_all('img')
    for image_tag in image_tags:
        alt_text = image_tag.get('alt', '')
        src = image_tag.get('src', '')
        image_links_with_alt_text.append({'src': src, 'alt_text': alt_text})

    # Get internal and external links with alt text
    internal_links_with_alt_text = []
    external_links_with_alt_text = []
    anchor_tags = soup.find_all('a')
    for anchor_tag in anchor_tags:
        alt_text = anchor_tag.get('alt', '')
        href = anchor_tag.get('href', '')

        if href.startswith('#') or href.startswith('tel:') or href.startswith('mailto:'):
            continue

        if href.startswith(('http://', 'https://')):
            external_links_with_alt_text.append({'url': href, 'alt_text': alt_text})
        else:
            internal_url = urljoin(base_url, href)
            internal_links_with_alt_text.append({'url': internal_url, 'alt_text': alt_text})

    # Get the word count and common words
    content_text = soup.get_text()
    words = content_text.split()
    word_count = len(words)

    # Remove stopwords
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    words = [word.lower() for word in words if word.lower() not in stop_words]

    # Count word frequencies
    word_frequencies = Counter(words)

    # Get the 10 most common words
    common_words = word_frequencies.most_common(10)

    # Return the SEO information
    seo_info = {
        'Title': title,
        'Meta Description': meta_description,
        'Headings': headings,
        'Image Links with Alt Text': image_links_with_alt_text,
        'Internal Links with Alt Text': internal_links_with_alt_text,
        'External Links with Alt Text': external_links_with_alt_text,
        'Word Count': word_count,
        'Common Words': common_words
    }
    return seo_info

# Example usage
url = 'https://lioltu.com.au/'  # Replace with the desired website URL
seo_info = get_seo_information(url)

# Write the SEO information to a file
filename = url.split('//')[-1].split('/')[0] + '.txt'
with open(filename, 'w') as file:
    for key, value in seo_info.items():
        file.write(f'{key}:\n')
        if key == 'Headings':
            for heading in value:
                file.write(f'H{heading["level"]}: {heading["text"]}\n')
        elif key == 'Image Links with Alt Text':
            for link in value:
                file.write(f'Image Source: {link["src"]}\n')
                file.write(f'Alt Text: {link["alt_text"]}\n')
        elif key == 'Internal Links with Alt Text' or key == 'External Links with Alt Text':
            for link in value:
                file.write(f'URL: {link["url"]}\n')
                file.write(f'Alt Text: {link["alt_text"]}\n')
        elif key == 'Common Words':
            for word, frequency in value:
                file.write(f'{word}: {frequency}\n')
        else:
            file.write(f'{value}\n')
        file.write('\n')
