document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = "/api/v1";
    let accessToken = null;
    let pollInterval = null;

    // Page containers
    const authPage = document.getElementById('auth-page');
    const appPage = document.getElementById('app-page');

    // Auth forms & toggles
    const loginContainer = document.getElementById('login-container');
    const registerContainer = document.getElementById('register-container');
    const showRegisterLink = document.getElementById('show-register');
    const showLoginLink = document.getElementById('show-login');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutButton = document.getElementById('logout-button');

    // App elements
    const scrapeForm = document.getElementById('scrape-form');
    const scrapeButton = document.getElementById('scrape-button');
    const queryCard = document.getElementById('query-card');
    const queryForm = document.getElementById('query-form');
    const resultsContainer = document.getElementById('results-container');

    // --- UI & State Management ---

    const showToast = (message, isError = false) => {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${isError ? 'error' : 'success'}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    };

    const showPage = (pageName) => {
        authPage.classList.toggle('hidden', pageName === 'app');
        appPage.classList.toggle('hidden', pageName === 'auth');
    };

    const setScrapingState = (isScraping) => {
        scrapeButton.disabled = isScraping;
        scrapeButton.textContent = isScraping ? 'Scraping...' : 'Scrape';
        if (isScraping) {
            resultsContainer.innerHTML = '<p>Scraping in progress. Please wait...</p>';
            queryCard.classList.add('hidden');
        }
    };
    
    // --- API & Logic ---

    const displayResults = (data) => {
        if (!data || data.length === 0) {
            resultsContainer.innerHTML = '<p>No data found. The scrape might have yielded no results or the parser needs adjustment.</p>';
            queryCard.classList.add('hidden');
            return;
        }
        queryCard.classList.remove('hidden');
        resultsContainer.innerHTML = `<h3 style="text-align: left; margin-bottom: 1rem;">Scraped Results (${data.length})</h3><div class="product-list"></div>`;
        const productList = resultsContainer.querySelector('.product-list');
        data.forEach(item => {
            const card = document.createElement('div');
            card.className = 'product-card';
            const price = item.price ? `$${item.price.toFixed(2)}` : 'N/A';
            const image = item.image_url ? `<img src="${item.image_url}" alt="${item.title}" onerror="this.style.display='none'">` : '';
            card.innerHTML = `${image}<h4><a href="${item.url}" target="_blank">${item.title}</a></h4><p>${price}</p>`;
            productList.appendChild(card);
        });
    };

    const pollTaskStatus = async (taskId) => {
        pollInterval = setInterval(async () => {
            try {
                // --- THIS IS THE CORRECTED URL ---
                const response = await fetch(`${API_BASE_URL}/scraping/scrape/status/${taskId}`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Server returned a non-JSON error' }));
                    throw new Error(errorData.detail || 'Server error while checking status.');
                }
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    clearInterval(pollInterval);
                    setScrapingState(false);
                    showToast('Scraping successful!', false);
                    displayResults(result.data);
                } else if (result.status === 'failed') {
                    clearInterval(pollInterval);
                    setScrapingState(false);
                    showToast(`Scraping failed: ${result.error}`, true);
                    resultsContainer.innerHTML = '';
                }
            } catch (error) {
                clearInterval(pollInterval);
                setScrapingState(false);
                showToast(error.message, true);
            }
        }, 3000);
    };

    // --- Event Handlers (No changes needed here) ---
    showRegisterLink.addEventListener('click', (e) => { e.preventDefault(); loginContainer.classList.add('hidden'); registerContainer.classList.remove('hidden'); });
    showLoginLink.addEventListener('click', (e) => { e.preventDefault(); registerContainer.classList.add('hidden'); loginContainer.classList.remove('hidden'); });
    registerForm.addEventListener('submit', async (e) => { e.preventDefault(); const email = document.getElementById('register-email').value; const password = document.getElementById('register-password').value; try { const response = await fetch(`${API_BASE_URL}/users/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Registration failed'); showToast('Registration successful! Please log in.'); showLoginLink.click(); } catch (error) { showToast(error.message, true); } });
    loginForm.addEventListener('submit', async (e) => { e.preventDefault(); const email = document.getElementById('login-email').value; const password = document.getElementById('login-password').value; const formData = new FormData(); formData.append('username', email); formData.append('password', password); try { const response = await fetch(`${API_BASE_URL}/users/login`, { method: 'POST', body: formData }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Login failed'); accessToken = data.access_token; showToast('Login successful!'); showPage('app'); } catch (error) { showToast(error.message, true); } });
    logoutButton.addEventListener('click', () => { accessToken = null; showToast('Logged out.'); showPage('auth'); });
    scrapeForm.addEventListener('submit', async (e) => { e.preventDefault(); const url = document.getElementById('scrape-url').value; setScrapingState(true); try { const response = await fetch(`${API_BASE_URL}/scraping/scrape`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` }, body: JSON.stringify({ url }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Failed to start job'); pollTaskStatus(data.task_id); } catch (error) { showToast(error.message, true); setScrapingState(false); } });
    queryForm.addEventListener('submit', async (e) => { e.preventDefault(); const question = document.getElementById('query-question').value; showToast('Asking AI...'); try { const response = await fetch(`${API_BASE_URL}/query/query`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` }, body: JSON.stringify({ question }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Query failed'); showToast(data.answer); } catch (error) { showToast(error.message, true); } });

    // Initial state
    showPage('auth');
});