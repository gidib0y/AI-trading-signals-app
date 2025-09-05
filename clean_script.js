// Clean, simplified JavaScript for trading interface
let currentMarket = 'stocks';
let currentTimeframe = '1h';

// Market data with organized categories
const marketData = {
    stocks: {
        name: 'STOCKS',
        icon: '📊',
        color: '#4CAF50',
        description: 'US Equities & ETFs',
        categories: {
            'NASDAQ': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC', 'CRM', 'ADBE'],
            'NYSE': ['JPM', 'JNJ', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'V', 'NKE', 'DIS', 'WMT', 'XOM'],
            'ETFs': ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'SLV', 'USO', 'TLT', 'VXX', 'PYPL', 'CVX', 'KO']
        }
    },
    forex: {
        name: 'FOREX',
        icon: '💱',
        color: '#2196F3',
        description: 'Currency Pairs',
        categories: {
            'MAJORS': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X'],
            'MINORS': ['EURGBP=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'EURAUD=X', 'GBPAUD=X', 'AUDNZD=X'],
            'EXOTICS': ['USDSEK=X', 'USDNOK=X', 'USDDKK=X', 'EURCHF=X', 'GBPCHF=X', 'USDZAR=X', 'USDTRY=X']
        }
    },
    crypto: {
        name: 'CRYPTO',
        icon: '₿',
        color: '#FFC107',
        description: 'Digital Assets',
        categories: {
            'MAJORS': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'SOL-USD'],
            'DEFI': ['UNI-USD', 'AAVE-USD', 'COMP-USD', 'MKR-USD', 'SUSHI-USD'],
            'LAYER1': ['ADA-USD', 'DOT-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD']
        }
    },
    futures: {
        name: 'FUTURES',
        icon: '⛽',
        color: '#FF9800',
        description: 'Commodities & Indices',
        categories: {
            'METALS': ['GC', 'SI', 'PL', 'PA', 'HG', 'AL', 'NI', 'ZN'],
            'ENERGY': ['CL', 'NG', 'HO', 'RB', 'BZ', 'QS', 'BZ=F'],
            'INDICES': ['ES', 'NQ', 'YM', 'RTY', 'SPX', 'NDX', 'DJI', 'RUT'],
            'AGRICULTURE': ['ZC', 'ZS', 'ZW', 'KC', 'CC', 'CT', 'SB', 'CC=F'],
            'BONDS': ['ZB', 'ZN', 'ZF', 'ZT', 'GE', 'TU', 'FV', 'TY']
        }
    },
    indices: {
        name: 'INDICES',
        icon: '📈',
        color: '#f44336',
        description: 'Market Indexes & ETFs',
        categories: {
            'US_INDICES': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO'],
            'INTERNATIONAL': ['EFA', 'EEM', 'ACWI', 'VT', 'VXUS', 'BND', 'TLT', 'IEF'],
            'VOLATILITY': ['VXX', 'UVXY', 'TVIX', 'VIXY', 'SHY', 'LQD', 'HYG', 'EMB']
        }
    },
    metals: {
        name: 'METALS',
        icon: '🥇',
        color: '#9C27B0',
        description: 'Precious Metals & Commodities',
        categories: {
            'PRECIOUS': ['GC', 'SI', 'PL', 'PA', 'GLD', 'SLV', 'PPLT', 'PALL'],
            'MINING': ['GDX', 'GDXJ', 'SIL', 'COPX', 'PICK', 'REMX', 'URA', 'LIT'],
            'AGRICULTURE': ['BAL', 'NIB', 'JO', 'CAFE', 'WEAT', 'CORN', 'SOYB', 'CANE']
        }
    }
};

// Core Functions
function selectMarket(market, element) {
    console.log('Selecting market:', market);
    currentMarket = market;
    
    // Update active market styling
    document.querySelectorAll('.market-card').forEach(card => {
        card.style.borderColor = 'rgba(255,255,255,0.2)';
        card.style.transform = 'scale(1)';
    });
    
    // Highlight the clicked market card
    if (element) {
        element.style.borderColor = marketData[market].color;
        element.style.transform = 'scale(1.05)';
    }
    
    // Show market symbols
    showMarketSymbols(market);
}

function showMarketSymbols(market) {
    console.log('Showing symbols for market:', market);
    
    const symbolsContainer = document.getElementById('market-symbols');
    const symbolsTitle = document.getElementById('market-symbols-title');
    const symbolsList = document.getElementById('symbols-list');
    
    if (!symbolsContainer || !symbolsTitle || !symbolsList) {
        console.log('Missing elements');
        return;
    }
    
    const marketInfo = marketData[market];
    const categories = marketInfo.categories;
    
    // Update title
    symbolsTitle.innerHTML = `${marketInfo.icon} ${marketInfo.name} Categories`;
    symbolsTitle.style.color = marketInfo.color;
    
    // Clear and populate symbols by category
    symbolsList.innerHTML = '';
    
    // Create category sections
    Object.entries(categories).forEach(([categoryName, symbols]) => {
        // Create category header
        const categoryHeader = document.createElement('div');
        categoryHeader.style.cssText = `
            background: linear-gradient(135deg, ${marketInfo.color}20, ${marketInfo.color}10);
            border-left: 4px solid ${marketInfo.color};
            border-radius: 6px;
            padding: 10px 15px;
            margin: 15px 0 10px 0;
            font-weight: bold;
            color: ${marketInfo.color};
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        categoryHeader.innerHTML = `📂 ${categoryName}`;
        symbolsList.appendChild(categoryHeader);
        
        // Create symbols grid for this category
        const categoryGrid = document.createElement('div');
        categoryGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px;
            margin-bottom: 20px;
        `;
        
        // Add symbols for this category
        symbols.slice(0, 8).forEach(symbol => {
            const symbolCard = document.createElement('div');
            symbolCard.style.cssText = `
                background: rgba(255,255,255,0.08);
                border: 1px solid ${marketInfo.color}30;
                border-radius: 6px;
                padding: 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                backdrop-filter: blur(5px);
                font-size: 0.85em;
            `;
            symbolCard.innerHTML = `
                <div style="font-weight: bold; color: ${marketInfo.color}; margin-bottom: 2px;">${symbol}</div>
                <div style="font-size: 0.7em; opacity: 0.7;">${categoryName}</div>
            `;
            symbolCard.onmouseover = () => {
                symbolCard.style.transform = 'scale(1.05)';
                symbolCard.style.borderColor = marketInfo.color;
                symbolCard.style.background = `rgba(${marketInfo.color.replace('#', '')}, 0.15)`;
            };
            symbolCard.onmouseout = () => {
                symbolCard.style.transform = 'scale(1)';
                symbolCard.style.borderColor = `${marketInfo.color}30`;
                symbolCard.style.background = 'rgba(255,255,255,0.08)';
            };
            symbolCard.onclick = () => {
                // Auto-fill the symbol analyzer
                const analyzeInput = document.getElementById('analyze-symbol');
                if (analyzeInput) {
                    analyzeInput.value = symbol;
                }
            };
            categoryGrid.appendChild(symbolCard);
        });
        
        symbolsList.appendChild(categoryGrid);
    });
    
    // Show the symbols container
    symbolsContainer.style.display = 'block';
}

function toggleCollapse(menuId) {
    const menu = document.getElementById(menuId);
    const arrow = menu.previousElementSibling.querySelector('.menu-arrow');
    
    if (menu.style.display === 'none' || menu.style.display === '') {
        menu.style.display = 'block';
        arrow.textContent = '▲';
    } else {
        menu.style.display = 'none';
        arrow.textContent = '▼';
    }
}

// Essential button functions
async function scanFullMarket() {
    console.log('Scanning full market...');
    const scannerDiv = document.getElementById('scanner-results');
    if (scannerDiv) {
        scannerDiv.innerHTML = '<div class="loading">🔍 Scanning entire market for trading signals...</div>';
    }
    
    try {
        const response = await fetch('/api/scan/full-market');
        const data = await response.json();
        
        if (scannerDiv) {
            scannerDiv.innerHTML = `
                <div style="color: #4CAF50; font-weight: bold; margin-bottom: 10px;">
                    ✅ Market scan completed! Found ${data.signals?.length || 0} signals
                </div>
                <div style="font-size: 0.9em; color: #ccc;">
                    ${data.message || 'Market analysis complete'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Scan error:', error);
        if (scannerDiv) {
            scannerDiv.innerHTML = '<div style="color: #f44336;">❌ Error scanning market</div>';
        }
    }
}

async function analyzeCustomSymbol() {
    const symbolInput = document.getElementById('analyze-symbol');
    const symbol = symbolInput?.value?.trim();
    
    if (!symbol) {
        alert('Please enter a symbol to analyze');
        return;
    }
    
    console.log('Analyzing symbol:', symbol);
    const analyzerDiv = document.getElementById('analyzer-results');
    if (analyzerDiv) {
        analyzerDiv.innerHTML = `<div class="loading">📊 Analyzing ${symbol}...</div>`;
    }
    
    try {
        const response = await fetch(`/api/analyze/${symbol}`);
        const data = await response.json();
        
        if (analyzerDiv) {
            analyzerDiv.innerHTML = `
                <div style="color: #2196F3; font-weight: bold; margin-bottom: 10px;">
                    📊 Analysis for ${symbol}
                </div>
                <div style="font-size: 0.9em; color: #ccc;">
                    ${data.message || 'Analysis complete'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Analysis error:', error);
        if (analyzerDiv) {
            analyzerDiv.innerHTML = '<div style="color: #f44336;">❌ Error analyzing symbol</div>';
        }
    }
}

async function getSignals() {
    console.log('Getting live signals...');
    const signalsDiv = document.getElementById('signals-display');
    if (signalsDiv) {
        signalsDiv.innerHTML = '<div class="loading">📈 Getting live trading signals...</div>';
    }
    
    try {
        const response = await fetch('/api/live/signals');
        const data = await response.json();
        
        if (signalsDiv) {
            signalsDiv.innerHTML = `
                <div style="color: #9C27B0; font-weight: bold; margin-bottom: 10px;">
                    📈 Live Signals
                </div>
                <div style="font-size: 0.9em; color: #ccc;">
                    ${data.message || 'Live signals loaded'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Signals error:', error);
        if (signalsDiv) {
            signalsDiv.innerHTML = '<div style="color: #f44336;">❌ Error loading signals</div>';
        }
    }
}

async function createCharts() {
    console.log('Creating charts...');
    alert('Charts functionality coming soon!');
}

async function getSummary() {
    console.log('Getting market summary...');
    alert('Market summary functionality coming soon!');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Trading interface loaded successfully!');
    
    // Set default market selection
    const firstMarketCard = document.querySelector('.market-card');
    if (firstMarketCard) {
        selectMarket('stocks', firstMarketCard);
    }
});
