let currentPage = 1; 

const API_BASE_URL = "https://movie-recommendation-system-ten.vercel.app";
const loadingMessage = document.getElementById("loading");
// Function to fetch movie recommendations based on title
function getMovieRecommendations() {
    let movieTitle = document.getElementById('movie-input').value.trim();

    if (!movieTitle) {
        console.error("Error: No movie title provided");
        return;
    }
    showLoading();
    fetch(`${API_BASE_URL}/recommend/movie?title=${encodeURIComponent(movieTitle)}&page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            hideLoading(); // Hide loading message
            displayResults(data);
        })
        .catch(error => {
            hideLoading();
            console.error("Fetch error:", error);
        });
}

// Function to fetch recommendations based on genre
function getGenreRecommendations() {
    let genre = document.getElementById('genre-input').value.trim();

    if (!genre) {
        console.error("Error: No genre provided");
        return;
    }

    showLoading();

    fetch(`${API_BASE_URL}/recommend/genre?genre=${encodeURIComponent(genre)}&page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            displayResults(data);
        })
        .catch(error => {
            hideLoading();
            console.error("Fetch error:", error);
        });
}

// Function to fetch recommendations based on Letterboxd username
function getLetterboxdRecommendations() {
    let username = document.getElementById('letterboxd-input').value.trim();

    if (!username) {
        alert("Please enter a Letterboxd username.");
        return;
    }

    showLoading();

    fetch(`${API_BASE_URL}/recommend/letterboxd?username=${encodeURIComponent(username)}&page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            console.log("Movies data:", data);
            if (data.error) {
                displayError(data.error);
            } else {
                console.log("Pagination Data:", data.current_page, data.previous_page, data.next_page);
                currentPage = data.current_page || 1;
                displayResults({ results: data.recommendations });
                addPaginationButtons(data);
            }
        })
        .catch(error => {
            hideLoading();
            console.error("Fetch error:", error);
        });
}


// Function to display results in a table
function displayResults(data) {
    console.log("Movies data:", data);

    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = ""; // Clear previous results

    if (!data.results || !Array.isArray(data.results) || data.results.length === 0) {
        resultsContainer.innerHTML = "<p>No results found</p>";
        return;
    }

    // Create table structure
    const table = document.createElement("table");
    table.setAttribute("id", "results-table");

    // Create table header
    const thead = document.createElement("thead");
    thead.innerHTML = `
        <tr>
            <th>Title (Year)</th>
            <th>Genres</th>
            <th>IMDb Rating</th>
        </tr>
    `;
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement("tbody");
    data.results.forEach(movie => {
        const title = movie.title || "Unknown Title";
        const year = movie.year || "Unknown Year";
        const genres = movie.genre ? movie.genre.join(", ") : "N/A";
        const rating = movie.rating !== undefined ? movie.rating : "N/A";

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${title} (${year})</td>
            <td>${genres}</td>
            <td style="text-align: center;">${rating}</td>
        `;
        tbody.appendChild(row);
    });

    table.appendChild(tbody);

    // Wrap table in a div for spacing
    const tableWrapper = document.createElement("div");
    tableWrapper.className = "results-container";
    tableWrapper.appendChild(table);

    resultsContainer.appendChild(tableWrapper);

    // Add Pagination Buttons
    addPaginationButtons(data);
}

// Function to add Next and Previous pagination buttons
function addPaginationButtons(data) {
    const paginationContainer = document.getElementById("pagination-container");
    paginationContainer.innerHTML = ""; // Clear previous buttons

    const prevButton = document.createElement("button");
    prevButton.textContent = "Previous";
    prevButton.disabled = !data.previous_page;
    prevButton.onclick = () => {
        if (data.previous_page) {
            currentPage = data.previous_page;
            reloadCurrentRecommendations();
        }
    };

    const nextButton = document.createElement("button");
    nextButton.textContent = "Next";
    nextButton.disabled = !data.next_page;
    nextButton.onclick = () => {
        if (data.next_page) {
            currentPage = data.next_page;
            reloadCurrentRecommendations();
        }
    };

    paginationContainer.appendChild(prevButton);
    paginationContainer.appendChild(document.createTextNode(` Page ${data.current_page} `));
    paginationContainer.appendChild(nextButton);
}


// Function to reload recommendations based on last used input
function reloadCurrentRecommendations() {
    const movieTitle = document.getElementById('movie-input')?.value.trim();
    const genre = document.getElementById('genre-input')?.value.trim();
    const username = document.getElementById('letterboxd-input')?.value.trim();

    if (movieTitle) {
        getMovieRecommendations();
    } else if (genre) {
        getGenreRecommendations();
    } else if (username) {
        getLetterboxdRecommendations();
    }
}

function showLoading() {
    loadingMessage.style.display = "block";
    document.getElementById("results").innerHTML = ""; // Clear previous results
}

// Function to hide loading message
function hideLoading() {
    loadingMessage.style.display = "none";
}