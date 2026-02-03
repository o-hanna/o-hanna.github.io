import json
import os
import html
from datetime import datetime

# --- CONFIGURATION ---
BASE_URL = "https://o-hanna.github.io" 
# ---------------------

JSON_PATH = 'data/publications.json'
TEMPLATE_PATH = 'template.html'
OUTPUT_DIR = 'publications'

def generate_pages():
    # 1. Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    valid_filenames = set()
    sitemap_urls = []

    print(f"Found {len(papers)} papers. Processing...")

    for paper in papers:
        if paper.get('create_page', False):
            filename = f"{paper['id']}.html"
            valid_filenames.add(filename)
            
            raw_pdf_link = paper.get('pdf_link', '')
            
            # --- FIX: URL Logic for Static Pages ---
            # 1. For Metadata (Needs Absolute URL):
            absolute_pdf_url = ""
            if raw_pdf_link:
                if raw_pdf_link.startswith(('http://', 'https://')):
                    absolute_pdf_url = raw_pdf_link
                else:
                    # Clean path relative to root
                    clean_pdf_path = raw_pdf_link.replace('../', '').replace('./', '').lstrip('/')
                    absolute_pdf_url = f"{BASE_URL}/{clean_pdf_path}"

            # 2. For the "Read PDF" Button (Needs Relative URL):
            # If we are in /publications/ folder, and the PDF is in /publications/pdfs/
            # We need the link to be just "pdfs/paper.pdf", not "publications/pdfs/paper.pdf"
            display_pdf_link = raw_pdf_link
            if raw_pdf_link and not raw_pdf_link.startswith(('http://', 'https://')):
                if raw_pdf_link.startswith('publications/'):
                    display_pdf_link = raw_pdf_link.replace('publications/', '', 1)

            # --- HTML Escaping ---
            safe_title = html.escape(paper['title'])
            safe_authors = html.escape(', '.join(paper['authors']))
            safe_venue = html.escape(paper['venue'])
            safe_abstract = html.escape(paper.get('abstract', ''))
            safe_year = str(paper['year'])

            # Metadata
            meta_tags = f"""
    <meta name="citation_title" content="{safe_title}">
    <meta name="citation_author" content="{'; '.join(paper['authors'])}">
    <meta name="citation_publication_date" content="{safe_year}">
    <meta name="citation_conference_title" content="{safe_venue}">
    <meta name="description" content="{safe_abstract[:160]}...">
            """
            if absolute_pdf_url:
                meta_tags += f'\n    <meta name="citation_pdf_url" content="{absolute_pdf_url}">'

            # Fill Template
            html_content = template.replace('{{TITLE}}', paper['title'])
            html_content = html_content.replace('{{META_TAGS}}', meta_tags)
            html_content = html_content.replace('{{AUTHORS}}', safe_authors)
            html_content = html_content.replace('{{VENUE}}', f"{safe_venue} ({safe_year})")
            html_content = html_content.replace('{{ABSTRACT}}', paper.get('abstract', ''))
            html_content = html_content.replace('{{BIBTEX}}', paper.get('bibtex', ''))
            
            if raw_pdf_link:
                # Use the corrected 'display_pdf_link' here
                pdf_btn = f'<a href="{display_pdf_link}" class="btn-action" target="_blank">Read PDF</a>'
            else:
                pdf_btn = ''
            html_content = html_content.replace('{{PDF_BUTTON}}', pdf_btn)

            # Write file
            filepath = f"{OUTPUT_DIR}/{filename}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            sitemap_urls.append(f"{BASE_URL}/publications/{filename}")

    generate_sitemap(sitemap_urls)
    cleanup_orphans(valid_filenames)

def generate_sitemap(urls):
    urls.insert(0, f"{BASE_URL}/index.html")
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{url}</loc>\n'
        sitemap_content += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_content += '  </url>\n'
    sitemap_content += '</urlset>'
    
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print("Generated sitemap.xml")

def cleanup_orphans(valid_filenames):
    for existing_file in os.listdir(OUTPUT_DIR):
        if existing_file.endswith(".html"):
            if existing_file not in valid_filenames:
                full_path = os.path.join(OUTPUT_DIR, existing_file)
                os.remove(full_path)
                print(f"Deleted orphan file: {existing_file}")

if __name__ == "__main__":
    generate_pages()
