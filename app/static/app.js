document.addEventListener('DOMContentLoaded', () => {
  const propertiesGrid = document.getElementById('propertiesGrid');
  const propertiesCount = document.getElementById('propertiesCount');
  const searchForm = document.getElementById('searchForm');
  const maxRent = document.getElementById('maxRent');
  const rentValue = document.getElementById('rentValue');
  const calcModal = document.getElementById('calcModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalBody = document.getElementById('modalBody');
  const aiForm = document.getElementById('aiForm');
  const aiQuestion = document.getElementById('aiQuestion');
  const aiAnswer = document.getElementById('aiAnswer');
  const refreshListings = document.getElementById('refreshListings');
  let currentProperties = [];
  const currency = new Intl.NumberFormat('en-IN');
  const money = (value) => `₹${currency.format(value)}`;

  function appendText(parent, tag, text, className) {
    const element = document.createElement(tag);
    element.textContent = text;
    if (className) element.className = className;
    parent.appendChild(element);
    return element;
  }

  function renderProperties(properties) {
    currentProperties = properties;
    propertiesCount.textContent = `${properties.length} live ${properties.length === 1 ? 'home' : 'homes'} · refreshed ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    propertiesGrid.replaceChildren();
    if (properties.length === 0) {
      appendText(propertiesGrid, 'p', 'No homes match those filters. Try widening your budget or neighbourhood.', 'empty-state');
      return;
    }
    properties.forEach((property) => {
      const card = document.createElement('article'); card.className = 'property-card';
      const header = document.createElement('div'); header.className = 'card-header';
      const titleBlock = document.createElement('div'); appendText(titleBlock, 'h3', property.title, 'card-title'); appendText(titleBlock, 'p', `● ${property.area}`, 'card-area');
      const badge = document.createElement('span'); badge.className = 'badge-tag'; badge.textContent = `${property.bhk} BHK`; header.append(titleBlock, badge); card.appendChild(header);
      const costs = document.createElement('div'); costs.className = 'cost-row';
      [['Monthly rent', money(property.rent_monthly)], ['Deposit', money(property.deposit)], ['Maintenance', money(property.maintenance)]].forEach(([label, value]) => { const item = document.createElement('div'); item.className = 'cost-item'; appendText(item, 'span', label); appendText(item, 'strong', value); costs.appendChild(item); }); card.appendChild(costs);
      const meta = document.createElement('div'); meta.className = 'meta-info'; appendText(meta, 'p', `${property.furnishing} · ${property.built_up_sqft} sq ft`); appendText(meta, 'p', `Metro: ${property.nearest_metro} (${property.metro_distance_km} km)`); const water = document.createElement('p'); const waterLabel = document.createElement('strong'); waterLabel.textContent = 'Water reliability: '; water.append(waterLabel, `${property.locality_metrics.water_score}/5 · ${property.locality_metrics.green_cover} greenery`); meta.appendChild(water); card.appendChild(meta);
      const commute = document.createElement('div'); commute.className = 'commute-list'; appendText(commute, 'div', 'COMMUTE ESTIMATES', 'commute-heading');
      property.work_commutes.slice(0, 3).forEach((route) => { const row = document.createElement('div'); row.className = 'commute-item'; appendText(row, 'span', route.destination); appendText(row, 'span', `~${route.travel_time_mins} min · ${route.mode}`, 'commute-time'); commute.appendChild(row); }); card.appendChild(commute);
      appendText(card, 'p', property.area_character, 'area-character');
      const actions = document.createElement('div'); actions.className = 'actions-row'; const map = document.createElement('a'); map.className = 'btn-secondary'; map.href = property.google_maps_url; map.target = '_blank'; map.rel = 'noopener'; map.textContent = 'View map ↗'; const calculator = document.createElement('button'); calculator.className = 'btn-secondary btn-accent'; calculator.type = 'button'; calculator.textContent = 'Cost breakdown'; calculator.addEventListener('click', () => openCostCalculator(property)); actions.append(map, calculator); card.appendChild(actions); propertiesGrid.appendChild(card);
    });
  }

  async function fetchProperties() {
    const params = new URLSearchParams();
    const values = { bhk: document.getElementById('bhkFilter').value, max_rent: maxRent.value, area: document.getElementById('areaFilter').value, work_location: document.getElementById('workLocation').value };
    Object.entries(values).forEach(([key, value]) => { if (value) params.set(key, value); });
    propertiesGrid.replaceChildren(); appendText(propertiesGrid, 'p', 'Finding the right fit...', 'empty-state');
    try { const response = await fetch(`/api/properties?${params}`); if (!response.ok) throw new Error('Could not load listings'); renderProperties(await response.json()); } catch (error) { propertiesGrid.replaceChildren(); appendText(propertiesGrid, 'p', error.message, 'empty-state'); propertiesCount.textContent = 'Search unavailable'; }
  }

  async function syncAndFetch() {
    refreshListings.disabled = true;
    refreshListings.textContent = 'Syncing...';
    try {
      const syncResponse = await fetch('/api/sync', { method: 'POST' });
      if (!syncResponse.ok) {
        const error = await syncResponse.json();
        throw new Error(error.detail || 'Live sync unavailable');
      }
      await fetchProperties();
    } catch (error) {
      propertiesCount.textContent = error.message;
    } finally {
      refreshListings.disabled = false;
      refreshListings.textContent = 'Refresh ↻';
    }
  }

  async function openCostCalculator(property) {
    try {
      const response = await fetch('/api/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ rent_monthly: property.rent_monthly, deposit: property.deposit, maintenance: property.maintenance, brokerage: 0, agreement_charges: 1500 }) });
      if (!response.ok) throw new Error('Could not calculate costs'); const data = await response.json(); document.getElementById('modalTitle').textContent = property.title; modalBody.replaceChildren();
      const hero = document.createElement('div'); hero.className = 'modal-hero'; appendText(hero, 'p', 'Total initial move-in outlay'); appendText(hero, 'h3', money(data.total_initial_move_in_cost)); modalBody.appendChild(hero);
      const list = document.createElement('div'); list.className = 'breakdown-list'; [['Monthly total burn', `${money(data.total_monthly_burn)} / month`], ['Deposit multiplier', `${data.deposit_to_rent_ratio}x ${data.is_deposit_high ? '(high)' : '(fair standard)'}`], ['Annual cost projection', money(data.annual_cost_projection)], ['Estimated annual savings', money(data.savings_vs_market_avg)]].forEach(([label, value]) => { const row = document.createElement('div'); row.className = 'breakdown-row'; appendText(row, 'span', label); appendText(row, 'strong', value); list.appendChild(row); }); modalBody.appendChild(list); calcModal.hidden = false; closeModalBtn.focus();
    } catch (error) { propertiesCount.textContent = error.message; }
  }

  async function askAI(event) {
    event.preventDefault();
    aiAnswer.textContent = 'Thinking through the shortlist...';
    try {
      const response = await fetch('/api/ai/insight', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: aiQuestion.value, listing_ids: currentProperties.map((property) => property.id) }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'AI assistant is unavailable');
      aiAnswer.textContent = data.answer;
    } catch (error) { aiAnswer.textContent = error.message; }
  }

  function closeModal() { calcModal.hidden = true; }
  maxRent.addEventListener('input', () => { rentValue.textContent = money(Number(maxRent.value)); }); searchForm.addEventListener('submit', (event) => { event.preventDefault(); fetchProperties(); }); aiForm.addEventListener('submit', askAI); closeModalBtn.addEventListener('click', closeModal); calcModal.addEventListener('click', (event) => { if (event.target === calcModal) closeModal(); }); document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !calcModal.hidden) closeModal(); });
  refreshListings.addEventListener('click', syncAndFetch); setInterval(syncAndFetch, 5 * 60 * 1000);
  rentValue.textContent = money(Number(maxRent.value)); fetchProperties();
});