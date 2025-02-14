document.addEventListener('DOMContentLoaded', async () => {
    console.log("📌 Script Loaded - Waiting for DOM Content");

    const teamSelect = document.getElementById('team-select');
    const playerSelect = document.getElementById('player-select');
    const statsTableBody = document.getElementById('player-stats');
    const playerImage = document.getElementById('player-image');
    const playerName = document.getElementById('player-name');
    const playerMeta = document.getElementById('player-meta');
    const playerDetails = document.getElementById('player-details');
    const playerDraft = document.getElementById('player-draft');

    let allPlayers = [];

    /**
     * 📌 Fetch CSV data
     */
    async function fetchCSV() {
        try {
            console.log("🔄 Fetching CSV file...");
            const response = await fetch('docs/OHL_STATS/LeagueStats_2024_2025.csv');
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.text();
            return parseCSV(data);
        } catch (error) {
            console.error("❌ Error fetching CSV:", error);
            return [];
        }
    }

    /**
     * 📌 Parse CSV into JavaScript objects
     */
    function parseCSV(csvData) {
        const rows = csvData.split(/\r?\n/).filter(row => row.trim() !== "");
        if (rows.length < 2) {
            console.warn("⚠️ CSV file has no data or is improperly formatted.");
            return [];
        }

        const headers = rows[0].split(',').map(h => h.trim());
        console.log("🔍 Parsed CSV Headers:", headers);

        const players = rows.slice(1).map(row => {
            const values = row.split(',').map(v => v.trim());
            if (values.length !== headers.length) return null;

            let playerObj = {};
            headers.forEach((header, index) => {
                playerObj[header] = values[index] || "N/A"; // Default "N/A" for missing values
            });

            return playerObj;
        }).filter(p => p !== null);

        console.log("✅ Parsed Players:", players.length, "players loaded.");
        return players;
    }

    /**
     * 📌 Populate Team Dropdown
     */
    function populateTeamDropdown(players) {
        const teams = ["All Teams", ...new Set(players.map(player => player.Team).filter(team => team !== "N/A"))];
        teamSelect.innerHTML = teams.map(team => `<option value="${team}">${team}</option>`).join("");
    }

    /**
     * 📌 Populate Player Dropdown based on selected team
     */
    function populatePlayerDropdown(players, selectedTeam = "All Teams") {
        playerSelect.innerHTML = '<option value="">Select a player</option>';
        players
            .filter(player => selectedTeam === "All Teams" || player.Team === selectedTeam)
            .forEach(player => {
                if (player['Name'] && player['Player_ID']) {
                    const option = document.createElement('option');
                    option.value = player['Player_ID'];
                    option.textContent = player['Name'];
                    playerSelect.appendChild(option);
                }
            });
    }

    /**
     * 📌 Display Player Stats and Image when selected
     */
    function displayPlayerStats(playerId) {
        const player = allPlayers.find(p => p['Player_ID'] === playerId);
        statsTableBody.innerHTML = '';

        if (player) {
            playerImage.src = `https://assets.leaguestat.com/ohl/240x240/${player['Player_ID']}.jpg`;

            playerName.textContent = player['Name'] || 'Unknown Player';
            playerMeta.textContent = [
                player['Jersey_Number'] ? `#${player['Jersey_Number']}` : '',
                player['Pos'] ? player['Pos'] : '',
                player['Team'] ? `| ${player['Team']}` : ''
            ].filter(Boolean).join(' ');

            playerDetails.textContent = [
                player['Shoots'] ? `Shoots: ${player['Shoots']}` : '',
                player['Hgt'] ? `Height: ${player['Hgt']}` : '',
                player['Wgt'] ? `Weight: ${player['Wgt']}` : ''
            ].filter(Boolean).join(' | ');

            playerDraft.textContent = [
                player['Draft_Team'] ? `Draft: ${player['Draft_Team']}` : '',
                player['Draft_Year'] ? `(${player['Draft_Year']})` : '',
                player['Draft_Round'] ? `Round: ${player['Draft_Round']}` : '',
                player['Draft_Pos'] ? `(#${player['Draft_Pos']})` : ''
            ].filter(Boolean).join(' ');

            const selectedStats = ["GP", "G", "A", "PTS", "+/-"];
            statsTableBody.innerHTML = `<tr>${selectedStats.map(stat => `<td>${player[stat] || '0'}</td>`).join("")}</tr>`;
        }
    }

    /**
     * 📌 Event Listeners
     */
    teamSelect.addEventListener("change", () => {
        populatePlayerDropdown(allPlayers, teamSelect.value);
        playerSelect.value = ""; // Reset player selection when team changes
        statsTableBody.innerHTML = "";
        playerImage.src = "";
        playerName.textContent = "";
        playerMeta.textContent = "";
        playerDetails.textContent = "";
        playerDraft.textContent = "";
    });

    playerSelect.addEventListener("change", () => displayPlayerStats(playerSelect.value));

    // 📌 Load Data & Populate UI
    allPlayers = await fetchCSV();
    if (allPlayers.length > 0) {
        populateTeamDropdown(allPlayers);
        populatePlayerDropdown(allPlayers);
    }
});
