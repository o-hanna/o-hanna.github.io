document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling logic (Keep as is)
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-item');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (pageYOffset >= (sectionTop - 150)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').includes(current)) {
                link.classList.add('active');
            }
        });
    });

    if (document.getElementById('publication-list')) {
        loadPublications();
    }
});

async function loadPublications() {
    try {
        const response = await fetch('data/publications.json');
        const papers = await response.json();
        
        const container = document.getElementById('publication-list');
        container.innerHTML = '';

        // Iterate directly through the JSON array (preserving your JSON order)
        papers.forEach((paper, index) => {
            if (paper.hide_from_list) {
                return; 
            }
            
            const uniqueBibId = `bib-${index}`;
            
            // Link Logic
            let titleHtml = '';
            if (paper.create_page) {
                titleHtml = `<a href="publications/${paper.id}.html" class="pub-title-link">${paper.title}</a>`;
            } else if (paper.pdf_link) {
                titleHtml = `<a href="${paper.pdf_link}" target="_blank" class="pub-title-link">${paper.title}</a>`;
            } else {
                titleHtml = `<span class="pub-title-static">${paper.title}</span>`;
            }

            const pubCard = document.createElement('div');
            pubCard.className = 'pub-card';
            
            // Added Year next to Venue inside the <p class="venue"> tag
            pubCard.innerHTML = `
                <div class="pub-content">
                    <h4>${titleHtml}</h4>
                    <p class="authors">${paper.authors.join(", ")}</p>
                    <p class="venue">${paper.venue} <strong>(${paper.year})</strong></p>
                </div>
                <div class="pub-actions">
                    ${paper.pdf_link ? `<a href="${paper.pdf_link}" class="btn-link" target="_blank">PDF</a>` : ''}
                    ${paper.create_page ? `<a href="publications/${paper.id}.html" class="btn-link">Details</a>` : ''}
                    <button class="btn-bib" onclick="toggleBib('${uniqueBibId}')">BibTeX</button>
                </div>
                <div id="${uniqueBibId}" class="bibtex-hidden">${paper.bibtex}</div>
            `;
            container.appendChild(pubCard);
        });

    } catch (error) {
        console.error('Error loading publications:', error);
        document.getElementById('publication-list').innerHTML = '<p>Error loading publications.</p>';
    }
}

function toggleBib(id) {
    document.querySelectorAll('.bibtex-hidden').forEach(el => {
        if (el.id !== id) el.style.display = 'none';
    });
    const el = document.getElementById(id);
    el.style.display = el.style.display === 'block' ? 'none' : 'block';
}
