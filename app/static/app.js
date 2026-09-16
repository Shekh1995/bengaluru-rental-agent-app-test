document.addEventListener('DOMContentLoaded', () => {
  const propertiesGrid = document.getElementById('propertiesGrid');
  const propertiesCount = document.getElementById('propertiesCount');
  const searchForm = document.getElementById('searchForm');
  const calcModal = document.getElementById('calcModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalBody = document.getElementById('modalBody');

  async function fetchProperties() {
    const bhk = document.getElementById('bhkFilter').value;
    const maxRent = document.getElementById('maxRent').value;
    const area = document.getElementById('areaFilter').value;
    const workLocation = document.getElementById('workLocation').value;

    const params = new URLSearchParams();
    if (bhk) params.append('bhk', bhk);
    if (maxRent) params.append('max_rent', maxRent);
    if (area) params.append('area', area);
    if (workLocation) params.append('work_location', workLocation);

    try {
      propertiesGrid.innerHTML = '<p style="color: #94a3b8;">Loading properties...</p>';
      const res = await fetch(`/api/properties?${params.toString()}`);
      const data = await res.json();
      renderProperties(data);
    } catch (err) {
      propertiesGrid.innerHTML = `<p style="color: #ef4444;">Error loading properties: ${err.message}</p>`;
    }
  }

  function renderProperties(properties) {
    propertiesCount.textContent = `Showing ${properties.length} verified value-optimized properties across Bengaluru`;

    if (properties.length === 0) {
      propertiesGrid.innerHTML = '<p style="color: #94a3b8;">No properties matching your criteria. Try adjusting your rent or area filters.</p>';
      return;
    }

    propertiesGrid.innerHTML = properties.map(p => `
      <div class="property-card">
        <div>
          <div class="card-header">
            <div>
              <h4 class="card-title">${p.title}</h4>
              <p style="font-size: 0.85rem; color: #38bdf8;">📍 ${p.area}</p>
            </div>
            <span class="badge-tag">${p.bhk} BHK</span>
          </div>

          <div class="cost-row">
            <div class="cost-item">
              <span>Monthly Rent</span>
              <strong>₹${p.rent_monthly.toLocaleString()}</strong>
            </div>
            <div class="cost-item">
              <span>Deposit</span>
              <strong style="color: #94a3b8;">₹${p.deposit.toLocaleString()}</strong>
            </div>
            <div class="cost-item">
              <span>Maintenance</span>
              <strong style="color: #94a3b8;">₹${p.maintenance.toLocaleString()}</strong>
            </div>
          </div>

          <div class="meta-info">
            <p><strong>🛋️ Furnishing:</strong> ${p.furnishing} (${p.built_up_sqft} sqft)</p>
            <p><strong>🚗 Parking:</strong> ${p.parking}</p>
            <p><strong>🚇 Metro:</strong> ${p.nearest_metro} (${p.metro_distance_km} km)</p>
            <p><strong>💧 Water Reliability:</strong> ${p.locality_metrics.water_score}/5</p>
          </div>

          <div class="commute-list">
            <strong style="display: block; font-size: 0.75rem; color: #94a3b8; margin-bottom: 4px;">COMMUTE ESTIMATES:</strong>
            ${p.work_commutes.map(c => `
              <div class="commute-item">
                <span>${c.destination}</span>
                <span style="color: #38bdf8; font-weight: 600;">~${c.travel_time_mins} mins (${c.mode})</span>
              </div>
            `).join('')}
          </div>
        </div>

        <div class="actions-row">
          <a href="${p.google_maps_url}" target="_blank" class="btn-secondary">🗺️ View Map</a>
          <button class="btn-secondary btn-accent" onclick="openCostCalculator(${p.rent_monthly}, ${p.deposit}, ${p.maintenance}, '${p.title.replace(/'/g, "\\'")}')">💰 Move-in Calc</button>
        </div>
      </div>
    `).join('');
  }

  window.openCostCalculator = async function(rent, deposit, maintenance, title) {
    try {
      const res = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rent_monthly: rent,
          deposit: deposit,
          maintenance: maintenance,
          brokerage: 0,
          agreement_charges: 1500
        })
      });
      const data = await res.json();

      document.getElementById('modalTitle').textContent = `Move-in Breakdown: ${title}`;
      modalBody.innerHTML = `
        <div style="background: #0f172a; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
          <p style="color: #94a3b8; font-size: 0.85rem;">Total Initial Move-in Outlay</p>
          <h2 style="color: #10b981; font-size: 2rem;">₹${data.total_initial_move_in_cost.toLocaleString()}</h2>
          <p style="font-size: 0.8rem; color: #94a3b8;">(Includes Refundable Deposit + 1st Mo Rent + Maint + Agreement)</p>
        </div>

        <div style="font-size: 0.9rem; color: #e2e8f0; line-height: 1.8;">
          <p><strong>Monthly Total Burn:</strong> ₹${data.total_monthly_burn.toLocaleString()}/mo</p>
          <p><strong>Security Deposit Multiplier:</strong> ${data.deposit_to_rent_ratio}x Months Rent ${data.is_deposit_high ? '<span style="color: #f59e0b;">(High)</span>' : '<span style="color: #10b981;">(Fair Standard)</span>'}</p>
          <p><strong>Estimated Annual Savings vs. Tech Corridor Avg:</strong> <span style="color: #10b981; font-weight: 600;">₹${data.savings_vs_market_avg.toLocaleString()}/year</span></p>
        </div>
      `;
      calcModal.style.display = 'flex';
    } catch (err) {
      alert('Error calculating breakdown: ' + err.message);
    }
  };

  closeModalBtn.addEventListener('click', () => {
    calcModal.style.display = 'none';
  });

  window.addEventListener('click', (e) => {
    if (e.target === calcModal) calcModal.style.display = 'none';
  });

  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    fetchProperties();
  });

  // Initial load
  fetchProperties();
});
