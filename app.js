document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date-select');
    const gameContainer = document.getElementById('game-container');
    const resultsDiv = document.getElementById('results');
    const closeBtn = document.getElementById('close-btn');
    const popup = document.getElementById('game-popup');

    if (closeBtn) {
        closeBtn.addEventListener('click', closePopup);
    }

    dateInput.addEventListener('change', function () {
        resultsDiv.innerHTML = ''; 
        const selectedDate = this.value;

        fetch(`docs/JSON_DATA/${selectedDate}.json`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("No predictions available for the selected date!");
                }
                return response.json();
            })
            .then(games => {
                gameContainer.innerHTML = ''; 

                if (games.length === 0) {
                    gameContainer.innerHTML = '<p>No games available for this date.</p>';
                    return;
                }

                games.forEach(game => {
                    const gameBox = document.createElement('div');
                    gameBox.className = 'game-box';

                    gameBox.innerHTML = `
                        <div class="game-row">
                            <span class="team away-team">${game.away_team}</span>
                            <span class="vs">vs</span>
                            <span class="team home-team">${game.home_team}</span>
                        </div>
                        <button class="select-btn" data-home="${game.home_team}" data-away="${game.away_team}">SELECT</button>
                    `;

                    gameContainer.appendChild(gameBox);
                });

                document.querySelectorAll('.select-btn').forEach(button => {
                    button.addEventListener('click', (e) => {
                        const homeTeam = e.target.dataset.home;
                        const awayTeam = e.target.dataset.away;
                        showGameDetails(homeTeam, awayTeam, selectedDate);
                    });
                });
            })
            .catch(error => {
                console.error('Error loading game data:', error);
                gameContainer.innerHTML = `<p>${error.message}</p>`;
            });
    });

    function showGameDetails(homeTeam, awayTeam, selectedDate) {
        const filePath = `docs/JSON_DATA/${selectedDate}.json`;

        fetch(filePath)
            .then(response => response.json())
            .then(predictions => {
                const game = predictions.find(pred => pred.home_team === homeTeam && pred.away_team === awayTeam);

                if (game) {
                    const popupDetails = document.getElementById('popup-details');
                    popupDetails.innerHTML = `
                        <h2>${game.away_team}<br> vs<br> ${game.home_team}</h2>
                        <hr>
                        <p><strong>Predicted Winner:</strong> ${game.winner}</p>
                        <hr>
                        <p><strong>Odds:</strong><br> ${game.away_team}: ${game.odds[game.away_team]}<br> ${game.home_team}: ${game.odds[game.home_team]}</p>
                    `;

                    popup.style.display = 'flex';
                } else {
                    alert('No prediction data available for this game.');
                }
            })
            .catch(error => {
                console.error("Error loading game details:", error);
                alert('Error loading game details.');
            });
    }

    function closePopup() {
        popup.style.display = 'none';
    }
});