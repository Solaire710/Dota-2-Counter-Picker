$(document).ready(function() {
    $('#search-bar').on('input', function() {
        const query = $(this).val();
        
        $.ajax({
            url: '/search',
            method: 'GET',
            data: { q: query },
            success: function(data) {
                $('#results').empty(); // Clear previous results
                data.forEach(function(item) {
                    $('#results').append('<li>' + item + '</li>'); // Add new results
                });
            }
        });
    });
});
