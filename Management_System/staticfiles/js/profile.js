document.addEventListener('DOMContentLoaded', function() {
    const editBtn = document.getElementById('edit-btn');
    const saveBtn = document.getElementById('save-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const favGenreField = document.getElementById('fav_genre');
    const usernameField = document.getElementById('username');
    const libNumField = document.getElementById('lib_num');
    const form = document.getElementById('profile-form');
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    const closeModal = document.getElementById('close-modal');

    // Enable editing of the fields
    editBtn.addEventListener('click', function() {
        favGenreField.disabled = false;
        saveBtn.classList.remove('hidden');
        cancelBtn.classList.remove('hidden');
        editBtn.classList.add('hidden');
    });

    // Handle form submission for saving changes via AJAX
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form from submitting normally

        const favGenre = favGenreField.value;

        // Example: Submit changes via AJAX
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value
            },
            body: JSON.stringify({
                fav_genre: favGenre
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modalMessage.textContent = 'Profile updated successfully!';
            } else {
                modalMessage.textContent = 'Error updating profile. Please try again.';
            }
            modal.classList.remove('hidden');
            
            // Redirect to the profile page (whether success or failure)
            setTimeout(() => {
                window.location.href = data.redirect_url || window.location.href;
            }, 2000);  // Delay to show the modal message for 2 seconds
        })
        .catch(error => {
            // Handle errors (e.g., network issues)
            modalMessage.textContent = 'Error updating profile. Please try again.';
            modal.classList.remove('hidden');
            // Redirect even if there is an error
            setTimeout(() => {
                window.location.href = window.location.href; // Keep the user on the profile page
            }, 2000); // Same delay for the error case
        });
    });

    // Close modal after confirmation/error
    closeModal.addEventListener('click', function() {
        modal.classList.add('hidden');
    });

    // Cancel edit and restore original values
    cancelBtn.addEventListener('click', function() {
        favGenreField.value = favGenreField.dataset.originalValue;  // Reset to original value
        favGenreField.disabled = true;
        saveBtn.classList.add('hidden');
        cancelBtn.classList.add('hidden');
        editBtn.classList.remove('hidden');
    });
});