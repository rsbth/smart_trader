// Global variables
let activeRecommendations = [];
let activePositions = [];
let recentTrades = [];

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    // Set up refresh button
    document.getElementById('refresh-btn').addEventListener('click', refreshData);
    
    // Initial data load
    refreshData();
    
    // Set up auto-refresh every 5 minutes
    setInterval(refreshData, 5 * 60 * 1000);
});

async function refreshData() {
    try {
        // Show loading state
        document.getElementById('refresh-btn').disabled = true;
        
        // Fetch all data concurrently
        const [recommendations, positions, trades, portfolio] = await Promise.all([
            fetchRecommendations(),
            fetchPositions(),
            fetchRecentTrades(),
            fetchPortfolioValue()
        ]);
        
        // Update the UI
        updateRecommendations(recommendations);
        updatePositions(positions);
        updateRecentTrades(trades);
        updatePortfolioValue(portfolio);
    } catch (error) {
        console.error('Error refreshing data:', error);
        showError('Failed to refresh data. Please try again.');
    } finally {
        document.getElementById('refresh-btn').disabled = false;
    }
}

async function fetchRecommendations() {
    const response = await fetch('/api/recommendations');
    const data = await response.json();
    activeRecommendations = data;
    return data;
}

function updateRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '';
    
    recommendations.forEach(rec => {
        const card = createRecommendationCard(rec);
        container.appendChild(card);
    });
    
    if (recommendations.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center text-muted">
                <p>No active recommendations at the moment</p>
            </div>
        `;
    }
}

function createRecommendationCard(recommendation) {
    const div = document.createElement('div');
    div.className = 'col-md-6';
    
    const priorityClass = getPriorityClass(recommendation.priority);
    const actionClass = recommendation.action === 'BUY' ? 'success' : 'danger';
    
    div.innerHTML = `
        <div class="card recommendation-card ${priorityClass} h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">${recommendation.symbol}</h6>
                <span class="badge bg-${actionClass}">${recommendation.action}</span>
            </div>
            <div class="card-body">
                <div class="mb-2">
                    <small class="text-muted">Reasons:</small>
                    <ul class="mb-0 small">
                        ${recommendation.reasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                </div>
                <div class="mb-2">
                    <small class="text-muted">Quantity:</small>
                    <span class="ms-1">${recommendation.quantity}</span>
                </div>
                ${recommendation.stop_loss ? `
                    <div class="mb-2">
                        <small class="text-muted">Stop Loss:</small>
                        <span class="ms-1">₹${recommendation.stop_loss.toFixed(2)}</span>
                    </div>
                ` : ''}
                ${recommendation.target ? `
                    <div class="mb-2">
                        <small class="text-muted">Target:</small>
                        <span class="ms-1">₹${recommendation.target.toFixed(2)}</span>
                    </div>
                ` : ''}
            </div>
            <div class="card-footer">
                <button class="btn btn-sm btn-${actionClass} w-100" 
                        onclick="showTradeConfirmation('${recommendation.id}')">
                    Execute ${recommendation.action}
                </button>
            </div>
        </div>
    `;
    
    return div;
}

function getPriorityClass(priority) {
    if (priority >= 4) return 'priority-high';
    if (priority >= 2) return 'priority-medium';
    return 'priority-low';
}

async function showTradeConfirmation(recommendationId) {
    const recommendation = activeRecommendations.find(r => r.id === recommendationId);
    if (!recommendation) return;
    
    const modal = new bootstrap.Modal(document.getElementById('tradeModal'));
    const modalBody = document.querySelector('#tradeModal .modal-body');
    
    modalBody.innerHTML = `
        <div class="mb-3">
            <h6>Trade Details:</h6>
            <ul class="list-unstyled">
                <li><strong>Symbol:</strong> ${recommendation.symbol}</li>
                <li><strong>Action:</strong> ${recommendation.action}</li>
                <li><strong>Quantity:</strong> ${recommendation.quantity}</li>
                <li><strong>Type:</strong> Market Order</li>
                ${recommendation.stop_loss ? `<li><strong>Stop Loss:</strong> ₹${recommendation.stop_loss.toFixed(2)}</li>` : ''}
                ${recommendation.target ? `<li><strong>Target:</strong> ₹${recommendation.target.toFixed(2)}</li>` : ''}
            </ul>
        </div>
        <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle"></i>
            Please confirm that you want to execute this trade. This action cannot be undone.
        </div>
    `;
    
    const confirmBtn = document.getElementById('confirm-trade-btn');
    confirmBtn.onclick = () => executeTrade(recommendationId, modal);
    
    modal.show();
}

async function executeTrade(recommendationId, modal) {
    try {
        const response = await fetch('/api/execute-trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ recommendation_id: recommendationId })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showSuccess('Trade executed successfully!');
            modal.hide();
            refreshData();
        } else {
            throw new Error(result.error || 'Failed to execute trade');
        }
    } catch (error) {
        console.error('Error executing trade:', error);
        showError(error.message);
    }
}

function updatePositions(positions) {
    const container = document.getElementById('positions-container');
    container.innerHTML = positions.map(position => `
        <div class="position-item border-bottom py-2">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">${position.symbol}</h6>
                    <small class="text-muted">Qty: ${position.quantity}</small>
                </div>
                <div class="text-end">
                    <div class="fw-bold ${position.pnl >= 0 ? 'text-success' : 'text-danger'}">
                        ${position.pnl >= 0 ? '+' : ''}₹${position.pnl.toFixed(2)}
                    </div>
                    <small class="text-muted">Avg: ₹${position.average_price.toFixed(2)}</small>
                </div>
            </div>
        </div>
    `).join('') || '<p class="text-muted text-center">No active positions</p>';
}

function updateRecentTrades(trades) {
    const container = document.getElementById('trades-container');
    container.innerHTML = trades.map(trade => `
        <div class="trade-item border-bottom py-2">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">${trade.symbol}</h6>
                    <small class="text-muted">${new Date(trade.timestamp).toLocaleString()}</small>
                </div>
                <span class="badge bg-${trade.action === 'BUY' ? 'success' : 'danger'}">
                    ${trade.action}
                </span>
            </div>
        </div>
    `).join('') || '<p class="text-muted text-center">No recent trades</p>';
}

function updatePortfolioValue(portfolio) {
    const element = document.getElementById('portfolio-value');
    element.textContent = `Portfolio: ₹${portfolio.value.toFixed(2)}`;
}

function showError(message) {
    // Implement error notification
    alert(message);
}

function showSuccess(message) {
    // Implement success notification
    alert(message);
}
