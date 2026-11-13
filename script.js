document.addEventListener('DOMContentLoaded', () => {
  const mobileToggle = document.getElementById('mobileToggle');
  const superNav = document.getElementById('superNav');
  if (mobileToggle && superNav) {
    mobileToggle.addEventListener('click', () => superNav.classList.toggle('show'));
  }

  const tableBody = document.getElementById('paitoTableBody');
  const status = document.getElementById('paitoStatus');
  const rowCount = document.getElementById('paitoCount');
  const ticker = document.getElementById('liveTrack');
  if (!tableBody) return;

  const setError = (message) => {
    if (status) status.textContent = message;
    tableBody.replaceChildren();
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 7;
    cell.className = 'text-center text-muted py-4';
    cell.textContent = message;
    row.appendChild(cell);
    tableBody.appendChild(row);
  };

  fetch(`data/paito-sdy.json?t=${Date.now()}`, { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((data) => {
      const valid = Array.isArray(data.rows)
        && data.rows.length > 0
        && data.rows.every((row) => Array.isArray(row) && row.length === 7
          && row.every((value) => value === '' || /^\d{5}$/.test(value)));
      if (!valid) throw new Error('Format data tidak sesuai');

      const fragment = document.createDocumentFragment();
      data.rows.forEach((values) => {
        const row = document.createElement('tr');
        values.forEach((value) => {
          const cell = document.createElement('td');
          const number = document.createElement('span');
          number.className = 'paito-number';
          number.textContent = value || '—';
          cell.appendChild(number);
          row.appendChild(cell);
        });
        fragment.appendChild(row);
      });
      tableBody.replaceChildren(fragment);

      const fetched = new Date(data.fetched_at);
      const fetchedText = Number.isNaN(fetched.getTime())
        ? data.fetched_at
        : fetched.toLocaleString('id-ID', {
          timeZone: 'Asia/Jakarta', dateStyle: 'medium', timeStyle: 'short',
        }) + ' WIB';
      const sourceLink = document.getElementById('paitoSource');
      if (sourceLink) sourceLink.href = data.source_page;
      if (status) status.textContent = `Pembaruan otomatis terakhir: ${fetchedText}. Sumber: Angkanet.`;
      if (rowCount) rowCount.textContent = String(data.rows.length);
      if (ticker) ticker.textContent = `Riwayat Paito SDY · ${data.rows.length} baris · Diperbarui ${fetchedText} · Sumber Angkanet`;
    })
    .catch((error) => {
      console.error('Gagal memuat data Paito SDY:', error);
      setError('Data belum dapat dimuat. Coba muat ulang halaman nanti.');
    });
});
