let currentPage = 1;
const perPage = 5;
let totalPages = 1;

// Fetch characters with pagination
async function fetchCharacters(page = 1) {
  try {
    const res = await fetch(`/characters?page=${page}&per_page=${perPage}`);
    const data = await res.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    renderTable(data.data);
    currentPage = data.meta.page;
    totalPages = data.meta.total_pages;
    updatePaginationButtons();
  } catch (err) {
    console.error("Pagination error:", err);
  }
}

// Render table rows
function renderTable(chars) {
  const tbody = document.querySelector("#characterTable tbody");
  tbody.innerHTML = "";
  chars.forEach((c) => {
    tbody.innerHTML += `
      <tr>
        <td>${c.id}</td>
        <td><input value="${c.first_name}" class="form-control form-control-sm" id="fn_${c.id}"></td>
        <td><input value="${c.last_name}" class="form-control form-control-sm" id="ln_${c.id}"></td>
        <td><input value="${c.occupation || ""}" class="form-control form-control-sm" id="occ_${c.id}"></td>
        <td>
          <button class="btn btn-sm btn-success me-2" onclick="updateCharacter(${c.id})">Update</button>
          <button class="btn btn-sm btn-danger" onclick="deleteCharacter(${c.id})">Delete</button>
        </td>
      </tr>`;
  });
}

// Search by first or last name
async function searchCharacters() {
  const q = document.getElementById("searchInput").value.trim();
  if (!q) {
    currentPage = 1;
    return fetchCharacters(1);
  }

  try {
    let res = await fetch(`/characters/search?first_name=${q}`);
    let data = await res.json();

    // If no result by first name, try last name
    if (data.message || data.error) {
      res = await fetch(`/characters/search?last_name=${q}`);
      data = await res.json();
    }

    if (data.error || data.message) {
      alert(data.error || data.message);
      return;
    }

    renderTable(data);
    document.getElementById("pageIndicator").textContent = `Search Results`;
  } catch (err) {
    console.error("Search error:", err);
  }
}

// Update a character
async function updateCharacter(id) {
  const payload = {
    first_name: document.getElementById(`fn_${id}`).value,
    last_name: document.getElementById(`ln_${id}`).value,
    occupation: document.getElementById(`occ_${id}`).value,
  };

  try {
    const res = await fetch(`/characters/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    alert(result.message || result.error);
    fetchCharacters(currentPage);
  } catch (err) {
    console.error("Update error:", err);
  }
}

// Delete a character
async function deleteCharacter(id) {
  if (!confirm("Delete this character?")) return;
  try {
    const res = await fetch(`/characters/${id}`, { method: "DELETE" });
    const result = await res.json();
    alert(result.message || result.error);
    fetchCharacters(currentPage);
  } catch (err) {
    console.error("Delete error:", err);
  }
}

// Pagination controls
function nextPage() {
  if (currentPage < totalPages) {
    currentPage += 1;
    fetchCharacters(currentPage);
  }
}

function prevPage() {
  if (currentPage > 1) {
    currentPage -= 1;
    fetchCharacters(currentPage);
  }
}

function updatePaginationButtons() {
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const pageIndicator = document.getElementById("pageIndicator");

  prevBtn.disabled = currentPage === 1;
  nextBtn.disabled = currentPage === totalPages;

  pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
}


fetchCharacters();
