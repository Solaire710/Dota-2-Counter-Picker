const form = document.getElementById("heroForm");
const resultsDiv = document.getElementById("results");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  resultsDiv.innerHTML = "<p>Loading...</p>";

  const formData = new FormData(form);
  const heroes = [];
  for (let [_, value] of formData.entries()) {
    if (value.trim()) heroes.push(value.trim());
  }

  const response = await fetch("/get_counters", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({heroes})
  });

  if (!response.ok) {
    resultsDiv.innerHTML = "<p>Error fetching counters.</p>";
    return;
  }

  const data = await response.json();
  resultsDiv.innerHTML = "<h2>Top Counters</h2><ul>" +
    data.map(c => `<li>${c.hero}: ${c.avg_win_rate}%</li>`).join("") +
    "</ul>";
});
