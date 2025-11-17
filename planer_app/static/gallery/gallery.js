/**
 * Gallery Page JavaScript
 * Handles lazy loading of images and photo deletion
 */

// Simple Lazy Loading with Intersection Observer
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('.lazy-image');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy-image');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers
        lazyImages.forEach(function(img) {
            img.src = img.dataset.src;
        });
    }
});

/**
 * Delete a photo from the gallery
 * @param {number} id - The photo ID to delete
 */
async function deletePhoto(id) {
    if (!confirm('Are you sure you want to delete this photo?')) {
        return;
    }

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log("Deleting photo with id: " + id);

    const response = await fetch("", {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            id: id
        })
    });

    const data = await response.json();
    console.log(data);

    if (data.deleted == "true") {
        console.log("Delete successful, removing element");
        const element = document.getElementById("photo_" + id);

        // Add fade-out animation before removing
        element.style.transition = 'opacity 0.3s';
        element.style.opacity = '0';

        setTimeout(() => {
            element.remove();

            // Check if gallery is now empty
            const galleryGrid = document.querySelector('.gallery-grid');
            if (galleryGrid && galleryGrid.children.length === 0) {
                location.reload();
            }
        }, 300);
    }
}
