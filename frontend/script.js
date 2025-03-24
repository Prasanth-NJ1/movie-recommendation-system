
function getGenreRecommendations() {
    let genre = document.getElementById('genre-input').value;
    fetch("http://127.0.0.1:8090/recommend/genre?genre=" + genre)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => displayResults(data))
        .catch(error => console.error("Fetch error:", error));
}


function getLetterboxdRecommendations() {
    let username = document.getElementById('letterboxd-input').value.trim();

    if (!username) {
        alert("Please enter a Letterboxd username.");
        return;
    }

    fetch(`http://127.0.0.1:8090/recommend/letterboxd?username=${username}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                displayError(data.error);
            } else {
                displayResults({ results: data.recommendations });
            }
        })
        .catch(error => console.error("Fetch error:", error));
}

function getMovieRecommendations() {
    let movieTitle = document.getElementById('movie-input').value;  // ✅ Get input value

    if (!movieTitle) {  // ✅ Check if input is empty
        console.error("Error: No movie title provided");
        return;
    }

    fetch("http://127.0.0.1:8090/recommend/movie?title=" + encodeURIComponent(movieTitle)) 
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => displayResults(data))  // ✅ Pass data to display function
        .catch(error => console.error("Fetch error:", error));
}


function displayResults(data) {
    console.log("Movies data:", data);
  
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = ""; // Clear previous results
  
    if (!data.results || !Array.isArray(data.results) || data.results.length === 0) {
      resultsContainer.innerHTML = "<p>No results found</p>";
      return;
    }
  
    data.results.forEach(movieStr => {
      // Extract details from the string using regex or string splitting
      const titleMatch = movieStr.match(/Title: (.*?)\n/);
      const yearMatch = movieStr.match(/Year: (\d{4})\n?/);
      const genreMatch = movieStr.match(/Genre: (.*?)\n/);
      const ratingMatch = movieStr.match(/iMDb rating: ([0-9.]+)/);
  
      const title = titleMatch ? titleMatch[1] : "Unknown Title";
      const year = yearMatch ? yearMatch[1] : "Unknown Year";
      const genres = genreMatch ? genreMatch[1] : "N/A";
      const rating = ratingMatch ? ratingMatch[1] : "N/A";
  
      // Display the extracted movie details
      const movieElement = `
        <div>
          <p><strong>${title} (${year})</strong></p>
          <p><strong>Genres:</strong> ${genres}</p>
          <p><strong>IMDb Rating:</strong> ${rating}</p>
        </div>
      `;
      resultsContainer.innerHTML += movieElement;
    });
  }
  