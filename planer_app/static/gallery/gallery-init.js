/**
 * Gallery Library Initialization
 * Initializes AOS (Animate On Scroll) and Flatpickr date pickers
 */

// Track which libraries have loaded
let loadedLibraries = {
    flatpickr: false,
    aos: false
};

// Check if all libraries are loaded and initialize
function checkAndInitialize() {
    if (loadedLibraries.flatpickr && loadedLibraries.aos) {
        initializeLibraries();
    }
}

// Listen for script load events
document.getElementById('flatpickr-script').addEventListener('load', function() {
    loadedLibraries.flatpickr = true;
    checkAndInitialize();
});

document.getElementById('aos-script').addEventListener('load', function() {
    loadedLibraries.aos = true;
    checkAndInitialize();
});

/**
 * Initialize all external libraries
 */
function initializeLibraries() {
    // Initialize AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });

    // Initialize Flatpickr for "Date From" picker
    flatpickr("#date_from", {
        dateFormat: "Y-m-d",
        maxDate: "today",
        onChange: function(selectedDates, dateStr, instance) {
            // Update the "to" date picker's minDate
            const dateToInstance = document.querySelector("#date_to")._flatpickr;
            if (dateToInstance) {
                dateToInstance.set('minDate', dateStr);
            }
        }
    });

    // Initialize Flatpickr for "Date To" picker
    flatpickr("#date_to", {
        dateFormat: "Y-m-d",
        maxDate: "today",
        onChange: function(selectedDates, dateStr, instance) {
            // Update the "from" date picker's maxDate
            const dateFromInstance = document.querySelector("#date_from")._flatpickr;
            if (dateFromInstance) {
                dateFromInstance.set('maxDate', dateStr);
            }
        }
    });
}
