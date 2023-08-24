{/* <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script> */}

    $(document).ready(function() {
        var searchInput = $('#search-input');
        var suggestionsDiv = $('#suggestions');

        searchInput.on('input', function() {
            var term = $(this).val();
            if (term.length >= 1) {
                fetchSuggestions(term);
            } else {
                suggestionsDiv.empty().hide();
            }
        });

        function fetchSuggestions(term) {
            $.ajax({
                url: '/store/search_suggestions/',
                data: { 'term': term },
                success: function(data) {
                    showSuggestions(data.suggestions);
                }
            });
        }

        function showSuggestions(suggestions) {
            suggestionsDiv.empty();
            if (suggestions.length > 0) {
                suggestionsDiv.show();
                suggestionsDiv.addClass('search-style-2'); // Add the class to apply the styles
                var suggestionsList = $('<ul>');
        
                suggestions.forEach(function(suggestion) {
                    var suggestionItem = $('<li>' + suggestion + '</li>');
                    suggestionItem.on('click', function() {
                        searchInput.val(suggestion);
                        suggestionsDiv.hide();
                    });
        
                    suggestionsList.append(suggestionItem);
                });
        
                suggestionsDiv.empty().append(suggestionsList);
                var searchBarOffset = searchInput.offset();
                suggestionsDiv.css({
                    top: searchBarOffset.top + searchInput.outerHeight(),
                    left: searchBarOffset.left,
                    maxWidth: searchInput.outerWidth()
                });
            } else {
                suggestionsDiv.empty().hide();
            }
        }
        

        // Hide suggestions when clicking outside the search input or suggestions
        $(document).on('click', function(event) {
            if (!searchInput.is(event.target) && !suggestionsDiv.is(event.target) && suggestionsDiv.has(event.target).length === 0) {
                suggestionsDiv.hide();
            }
        });
});
