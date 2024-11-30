// Global variables for charts
let priceChart = null;

// Function to analyze a stock
async function analyzeStock() {
    const symbol = document.getElementById('stockSymbol').value;
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }

    showLoading(true);
    try {
        const response = await fetch(`/api/analyze/${symbol}`);
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Error:', error);
        alert('Error analyzing stock. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Function to update the UI with analysis results
function updateUI(data) {
    document.getElementById('analysisResults').style.display = 'block';
    document.getElementById('stockName').textContent = data.name;
    document.getElementById('currentPrice').textContent = `₹${data.current_price}`;

    updatePriceChart(data.price_history);
    updateTechnicalAnalysis(data.technical);
    updateFundamentalAnalysis(data.fundamental);
    updateSentimentAnalysis(data.sentiment);
    updateRecommendation(data.recommendation);
}

// Function to update the price chart
function updatePriceChart(priceData) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (priceChart) {
        priceChart.destroy();
    }

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: priceData.dates,
            datasets: [{
                label: 'Price',
                data: priceData.prices,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Price History'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Function to show/hide loading indicator
function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

// Function to execute a trade
async function executeTrade(action) {
    const symbol = document.getElementById('stockSymbol').value;
    if (!symbol) {
        alert('Please analyze a stock first');
        return;
    }

    const quantity = prompt('Enter quantity:', '1');
    if (!quantity || isNaN(quantity) || quantity <= 0) {
        alert('Please enter a valid quantity');
        return;
    }

    try {
        const response = await fetch('/api/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol: symbol,
                action: action,
                quantity: parseInt(quantity)
            })
        });

        const result = await response.json();
        if (result.success) {
            alert(`${action} order placed successfully!`);
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error executing trade. Please try again.');
    }
}

// Function to update technical analysis section
function updateTechnicalAnalysis(data) {
    const technicalDiv = document.getElementById('technical');
    if (!technicalDiv) return;

    let html = '<div class="row">';
    
    // Add technical indicators
    for (const [indicator, value] of Object.entries(data.indicators)) {
        html += `
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${indicator}</h5>
                        <p class="card-text">${value}</p>
                    </div>
                </div>
            </div>
        `;
    }

    html += '</div>';
    
    // Add patterns if available
    if (data.patterns && data.patterns.length > 0) {
        html += '<h4 class="mt-4">Patterns Detected</h4><ul>';
        data.patterns.forEach(pattern => {
            html += `<li>${pattern}</li>`;
        });
        html += '</ul>';
    }

    technicalDiv.innerHTML = html;
}

// Function to update fundamental analysis section
function updateFundamentalAnalysis(data) {
    const fundamentalDiv = document.getElementById('fundamental');
    if (!fundamentalDiv || !data) return;

    let html = '<div class="row">';
    
    // Add fundamental metrics
    for (const [metric, value] of Object.entries(data)) {
        html += `
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${metric}</h5>
                        <p class="card-text">${value}</p>
                    </div>
                </div>
            </div>
        `;
    }

    html += '</div>';
    fundamentalDiv.innerHTML = html;
}

// Function to update sentiment analysis section
function updateSentimentAnalysis(data) {
    const sentimentDiv = document.getElementById('sentiment');
    if (!sentimentDiv || !data) return;

    let html = `
        <div class="row">
            <div class="col-md-6">
                <h4>Market Sentiment</h4>
                <p>Overall: ${data.market_sentiment}</p>
                <p>Confidence: ${data.confidence}%</p>
            </div>
            <div class="col-md-6">
                <h4>Recent News</h4>
                <ul>
    `;

    data.news.forEach(item => {
        html += `<li>${item.title} - ${item.sentiment}</li>`;
    });

    html += '</ul></div></div>';
    sentimentDiv.innerHTML = html;
}

// Function to update recommendation section
function updateRecommendation(data) {
    const recommendationDiv = document.getElementById('recommendation');
    if (!recommendationDiv || !data) return;

    const signalClass = data.signal.toLowerCase() === 'buy' ? 'text-success' : 
                       data.signal.toLowerCase() === 'sell' ? 'text-danger' : 
                       'text-warning';

    let html = `
        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Trading Recommendation</h4>
                <p class="card-text">Signal: <span class="${signalClass} fw-bold">${data.signal}</span></p>
                <p class="card-text">Confidence: ${data.confidence}%</p>
                <p class="card-text">Reason: ${data.reason}</p>
                <div class="mt-3">
                    <button class="btn btn-success me-2" onclick="executeTrade('buy')">Buy</button>
                    <button class="btn btn-danger" onclick="executeTrade('sell')">Sell</button>
                </div>
            </div>
        </div>
    `;

    recommendationDiv.innerHTML = html;
}

// Initialize any necessary components when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here
    const stockSymbol = document.getElementById('stockSymbol');
    if (stockSymbol) {
        stockSymbol.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeStock();
            }
        });
    }
});
