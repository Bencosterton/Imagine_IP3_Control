// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    let selectedSource = null;
    let selectedDestination = null;
    let pokeMode = false;

    // Get the time
    function updateTimestamp() {
        const timestampElement = document.querySelector('.timestamp');
        
        function update() {
            const now = new Date();
            const formattedDate = now.toLocaleDateString('en-GB');
            const formattedTime = now.toLocaleTimeString('en-GB', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
            timestampElement.textContent = `${formattedDate} ${formattedTime}`;
        }
    
        update();
        setInterval(update, 1000);
    }

    // Search functionality
    function setupSearch(searchId, buttonClass, countId) {
        const searchInput = document.getElementById(searchId);
        const countDisplay = document.getElementById(countId);
        
        function updateCount() {
            const totalButtons = document.querySelectorAll(`.${buttonClass}`).length;
            const visibleButtons = document.querySelectorAll(`.${buttonClass}:not(.hidden)`).length;
            countDisplay.textContent = `${visibleButtons}/${totalButtons}`;
        }
        
        updateCount();
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            document.querySelectorAll(`.${buttonClass}`).forEach(btn => {
                const text = btn.textContent.toLowerCase();
                const isVisible = text.includes(searchTerm);
                btn.classList.toggle('hidden', !isVisible);
            });
            
            updateCount();
        });

        // Clear search
        function clearSearch() {
            document.querySelectorAll(`.${buttonClass}`).forEach(btn => {
                btn.classList.remove('hidden');
            });
            updateCount();
        }

        searchInput.addEventListener('search', function() {
            if (this.value === '') {
                clearSearch();
            }
        });

        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                clearSearch();
            }
        });
    }

    // Category functionality
    function initializeCategories() {
        // Source categories
        document.querySelectorAll('.category-buttons.sources .category-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const category = this.dataset.category;
                
                // Toggle active state
                document.querySelectorAll('.category-buttons.sources .category-btn').forEach(b => 
                    b.classList.remove('active'));
                this.classList.add('active');
                
                // Filter sources
                document.querySelectorAll('.source-btn').forEach(sourceBtn => {
                    if (category === 'all' || sourceBtn.dataset.categories.includes(category)) {
                        sourceBtn.classList.remove('hidden');
                    } else {
                        sourceBtn.classList.add('hidden');
                    }
                });
                
                const countDisplay = document.getElementById('source-count');
                const totalButtons = document.querySelectorAll('.source-btn').length;
                const visibleButtons = document.querySelectorAll('.source-btn:not(.hidden)').length;
                countDisplay.textContent = `${visibleButtons}/${totalButtons}`;
            });
        });

        // Destination categories
        document.querySelectorAll('.category-buttons.destinations .category-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const category = this.dataset.category;
                
                // Toggle active state
                document.querySelectorAll('.category-buttons.destinations .category-btn').forEach(b => 
                    b.classList.remove('active'));
                this.classList.add('active');
                
                // Filter destinations
                document.querySelectorAll('.destination-btn').forEach(destBtn => {
                    if (category === 'all' || destBtn.dataset.categories.includes(category)) {
                        destBtn.classList.remove('hidden');
                    } else {
                        destBtn.classList.add('hidden');
                    }
                });
                
                const countDisplay = document.getElementById('destination-count');
                const totalButtons = document.querySelectorAll('.destination-btn').length;
                const visibleButtons = document.querySelectorAll('.destination-btn:not(.hidden)').length;
                countDisplay.textContent = `${visibleButtons}/${totalButtons}`;
            });
        });
    }

    // Router status functionality
    function updateDestinationStatus(destination) {
        const btn = document.querySelector(`.destination-btn[data-destination="${destination}"]`);
        if (!btn) return;

        fetch(`/status/${destination}`)
            .then(response => response.json())
            .then(data => {
                if (selectedDestination === destination && data.source) {
                    const sourceBtn = document.querySelector(`.source-btn[data-source="${data.source}"]`);
                    if (data.source === 'HD-BARS') {
                        selectSource('HD-BARS', document.querySelector('.control-btn[data-source="HD-BARS"]'));
                    } else if (sourceBtn) {
                        selectSource(data.source, sourceBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error getting status:', error);
            });
    }

    // Pokemon functionality
    function initializePokemonMode() {
        const pokeCheckbox = document.getElementById('poke-mode');
        const sourcePoke = document.getElementById('source-poke');
        const destinationPoke = document.getElementById('destination-poke');

        pokeCheckbox.addEventListener('change', function() {
            pokeMode = this.checked;
            sourcePoke.classList.toggle('hidden', !pokeMode);
            destinationPoke.classList.toggle('hidden', !pokeMode);
            
            if (pokeMode) {
                if (!selectedSource) {
                    document.querySelector('#source-poke img').src = '/static/poke-sprite/A.png';
                }
                if (!selectedDestination) {
                    document.querySelector('#destination-poke img').src = '/static/poke-sprite/A.png';
                }
                if (selectedSource) {
                    updateSourcePokemon(selectedSource);
                }
                if (selectedDestination) {
                    updateDestinationPokemon(selectedDestination);
                }
            }
        });
    }

    function updateSourcePokemon(source) {
        if (!pokeMode) return;
        
        fetch(`/pokemon/source/${source}`)
            .then(response => response.json())
            .then(data => {
                const pokemonImg = document.querySelector('#source-poke img');
                if (data.pokemon_id) {
                    pokemonImg.src = `/static/poke-sprite/${data.pokemon_id}.png`;
                } else {
                    pokemonImg.src = '/static/poke-sprite/A.png';
                }
            })
            .catch(error => console.error('Error loading pokemon:', error));
    }

    function updateDestinationPokemon(destination) {
        if (!pokeMode) return;
        
        fetch(`/pokemon/destination/${destination}`)
            .then(response => response.json())
            .then(data => {
                const pokemonImg = document.querySelector('#destination-poke img');
                if (data.pokemon_id) {
                    pokemonImg.src = `/static/poke-sprite/${data.pokemon_id}.png`;
                } else {
                    pokemonImg.src = '/static/poke-sprite/A.png';
                }
            })
            .catch(error => console.error('Error loading pokemon:', error));
    }

    // Selection functionality
    function selectSource(source, buttonElement) {
        document.querySelectorAll('.source-btn, .control-btn').forEach(b => b.classList.remove('selected'));
        
        if (buttonElement) {
            buttonElement.classList.add('selected');
        }
        
        selectedSource = source;
        document.querySelector('#selected-source .selection-value').textContent = source;
        updateTakeButton();

        if (pokeMode) {
            updateSourcePokemon(source);
        }
    }

    function resetSelections() {
        document.querySelectorAll('.source-btn, .control-btn').forEach(btn => btn.classList.remove('selected'));
        document.querySelectorAll('.destination-btn').forEach(btn => btn.classList.remove('selected'));
        document.querySelector('#selected-source .selection-value').textContent = '';
        document.querySelector('#selected-destination .selection-value').textContent = '';
        if (pokeMode) {
            document.querySelector('#source-poke img').src = '/static/poke-sprite/A.png';
            document.querySelector('#destination-poke img').src = '/static/poke-sprite/A.png';
        }
        selectedSource = null;
        selectedDestination = null;
        updateTakeButton();
    }

    function updateTakeButton() {
        const takeButton = document.querySelector('.take-button');
        if (selectedSource && selectedDestination) {
            takeButton.classList.add('active');
        } else {
            takeButton.classList.remove('active');
        }
    }

    // Event Listeners
    document.querySelectorAll('.source-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            selectSource(this.dataset.source, this);
        });
    });
    
    document.querySelectorAll('.destination-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.destination-btn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            selectedDestination = this.dataset.destination;
            document.querySelector('#selected-destination .selection-value').textContent = selectedDestination;
            updateTakeButton();
            updateDestinationStatus(selectedDestination);
            if (pokeMode) {
                updateDestinationPokemon(selectedDestination);
            }
        });
    });

    document.getElementById('selected-source').addEventListener('click', function() {
        selectedSource = null;
        this.querySelector('.selection-value').textContent = '';
        document.querySelectorAll('.source-btn, .control-btn').forEach(btn => btn.classList.remove('selected'));
        if (pokeMode) {
            document.querySelector('#source-poke img').src = '/static/poke-sprite/A.png';
        }
        updateTakeButton();
    });

    document.getElementById('selected-destination').addEventListener('click', function() {
        selectedDestination = null;
        this.querySelector('.selection-value').textContent = '';
        document.querySelectorAll('.destination-btn').forEach(btn => btn.classList.remove('selected'));
        if (pokeMode) {
            document.querySelector('#destination-poke img').src = '/static/poke-sprite/A.png';
        }
        updateTakeButton();
    });

    document.querySelector('.take-button').addEventListener('click', function() {
        if (selectedSource && selectedDestination) {
            fetch('/route', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source: selectedSource,
                    destination: selectedDestination
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    resetSelections();
                } else {
                    alert('Route failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Route failed: Network error');
            });
        }
    });

    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            selectSource(this.dataset.source, this);
        });
    });

    // Initialize all components
    updateTimestamp();
    setupSearch('source-search', 'source-btn', 'source-count');
    setupSearch('destination-search', 'destination-btn', 'destination-count');
    initializeCategories();
    initializePokemonMode();
});
